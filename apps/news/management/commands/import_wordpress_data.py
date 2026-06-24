import logging
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

import bleach
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.utils import timezone, translation
from django.utils.html import strip_tags
from django.utils.text import slugify

from apps.comments.models import Comment
from apps.core.models import ImportSource, MediaAsset, Redirect, SiteSetting
from apps.core.wordpress_sql import iter_wordpress_rows
from apps.news.models import Category, Post, Tag
from apps.pages.models import Book, BookCategory, Page


SOURCES = [
    {
        "language": "en",
        "database": "gashuvyp_wp634",
        "prefix": "wp4r_",
        "domain": "https://yvesgashugi.org",
        "default_file": Path.home() / "Downloads" / "gashuvyp_wp634.sql",
    },
    {
        "language": "rw",
        "database": "gashuvyp_wp799",
        "prefix": "wpix_",
        "domain": "https://kiny.yvesgashugi.org",
        "default_file": Path.home() / "Downloads" / "gashuvyp_wp799.sql",
    },
    {
        "language": "fr",
        "database": "gashuvyp_wp804",
        "prefix": "wpyr_",
        "domain": "https://fra.yvesgashugi.org",
        "default_file": Path.home() / "Downloads" / "gashuvyp_wp804.sql",
    },
]

WANTED_TABLES = {
    "posts",
    "postmeta",
    "terms",
    "term_taxonomy",
    "term_relationships",
    "comments",
    "users",
    "usermeta",
    "options",
}

USEFUL_POSTMETA = {
    "_thumbnail_id",
    "_wp_attached_file",
    "_wp_attachment_image_alt",
    "_yoast_wpseo_title",
    "_yoast_wpseo_metadesc",
    "rank_math_title",
    "rank_math_description",
    "post_views_count",
    "_post_views_count",
    "views",
    "entry_views",
}

USEFUL_USERMETA = {"description", "first_name", "last_name", "nickname"}
USEFUL_OPTIONS = {
    "blogname",
    "blogdescription",
    "siteurl",
    "home",
    "admin_email",
    "WPLANG",
}

SUSPICIOUS_USERNAME_RE = re.compile(
    r"(hack|cache|backup|wprocket|shell|exploit|malware|^xadmin$|^mainhack$|"
    r"^admin(?:istrator|istrar|[_%0-9-]|$).*|^root$|^wadmin|^[a-z0-9]{18,}$)",
    re.I,
)

CATEGORY_ALIASES = {
    "church": {"church", "itorero", "eglise", "église"},
    "leadership": {"leadership", "ubuyobozi", "direction"},
    "family": {"family", "umuryango", "famille"},
    "constructive-criticism": {
        "constructive criticism",
        "kunenga byubaka",
        "critique constructive",
        "constructive-criticism",
    },
    "healing": {"healing", "isanamitima", "guerison", "guérison"},
    "books": {"books", "book", "ibitabo", "livres"},
    "events": {"events", "event", "ibirori", "evenements", "événements"},
}

PAGE_ALIASES = {
    "who-we-are": {"who-we-are", "about-us", "a-propos", "abo-turi-bo"},
    "our-history": {"our-history", "notre-histoire", "amateka-yacu"},
    "mission-and-vision": {
        "mission-and-vision",
        "statement-of-faith",
        "mission-et-vision",
        "intego-nicyerekezo",
    },
    "leadership": {"our-team", "leadership", "direction", "ubuyobozi"},
    "what-we-do": {"what-we-do", "what-we-do-2", "ce-que-nous-faisons", "ibyo-dukora"},
    "find-a-counsellor": {
        "find-a-counsellor",
        "trouver-un-conseiller",
        "shaka-umujyanama",
    },
    "contact-us": {"contact-us", "contactez-nous", "twandikire"},
    "donate": {"donate", "faire-un-don", "tanga-inkunga"},
    "website-policy": {"website-policy", "politique-du-site", "amabwiriza-yurubuga"},
    "books": {"books", "livres", "ibitabo"},
}

ALLOWED_TAGS = [
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "b",
    "em", "i", "u", "blockquote", "ul", "ol", "li", "a", "img", "figure",
    "figcaption", "table", "thead", "tbody", "tr", "th", "td", "iframe",
    "div", "span", "pre", "code",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height", "loading"],
    "iframe": ["src", "width", "height", "title", "allow", "allowfullscreen"],
    "div": ["dir"],
    "span": ["dir"],
    "*": ["lang"],
}


class Command(BaseCommand):
    help = "Import and merge the three legacy WordPress SQL dumps into Django."

    def add_arguments(self, parser):
        parser.add_argument("--english-sql", default=str(SOURCES[0]["default_file"]))
        parser.add_argument("--kinyarwanda-sql", default=str(SOURCES[1]["default_file"]))
        parser.add_argument("--french-sql", default=str(SOURCES[2]["default_file"]))
        parser.add_argument("--media-root", default="")
        parser.add_argument("--media-root-en", default="")
        parser.add_argument("--media-root-fr", default="")
        parser.add_argument("--media-root-rw", default="")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--no-backup", action="store_true")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.limit = max(options["limit"], 0)
        self.report = Counter()
        self.warnings = []
        self.errors = []
        self.object_maps = {}
        self.category_maps = {}
        self.tag_maps = {}
        self.user_maps = {}
        self.media_maps = {}
        self.loaded_sources = []
        self.log_path = self._configure_logging()

        paths = {
            "en": Path(options["english_sql"]),
            "rw": Path(options["kinyarwanda_sql"]),
            "fr": Path(options["french_sql"]),
        }
        media_roots = {
            language: Path(options[f"media_root_{language}"] or options["media_root"])
            if (options[f"media_root_{language}"] or options["media_root"])
            else None
            for language in ("en", "fr", "rw")
        }
        for source in SOURCES:
            source["path"] = paths[source["language"]]
            source["media_root"] = media_roots[source["language"]]
            if not source["path"].exists():
                raise CommandError(f"SQL dump not found: {source['path']}")

        self._log("Starting WordPress import")
        if self.dry_run:
            self._log("DRY RUN: no database or media changes will be made")
        elif not options["no_backup"]:
            self._backup_database()

        if options["reset"] and not self.dry_run:
            self._reset_previous_imports()

        if not self.dry_run:
            call_command("seed_site_pages", verbosity=0)

        for source in SOURCES:
            self.loaded_sources.append(self._load_source(source))

        if self.dry_run:
            self._dry_run_report()
            self._finish()
            return

        try:
            with transaction.atomic():
                for data in self.loaded_sources:
                    self._import_users(data)
                for data in self.loaded_sources:
                    self._import_taxonomies(data)
                for data in self.loaded_sources:
                    self._import_media(data)
                for data in self.loaded_sources:
                    self._import_pages(data)
                for data in self.loaded_sources:
                    self._import_posts(data)
                for data in self.loaded_sources:
                    self._link_page_parents(data)
                    self._import_comments(data)
                    self._import_books(data)
                self._import_site_settings()
                call_command("seed_site_pages", verbosity=0)
        except Exception as exc:
            self.errors.append(str(exc))
            logging.exception("Import failed")
            raise

        self._finish()

    def _configure_logging(self):
        log_dir = Path(settings.BASE_DIR) / "import_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"wordpress_import_{timestamp}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[logging.FileHandler(log_path, encoding="utf-8")],
            force=True,
        )
        return log_path

    def _log(self, message, style=None):
        logging.info(message)
        output = style(message) if style else message
        self.stdout.write(output)

    def _backup_database(self):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            self._log("Automatic backup skipped: database is not SQLite", self.style.WARNING)
            return
        source = Path(database["NAME"])
        if not source.exists():
            return
        backup_dir = Path(settings.BASE_DIR) / "import_logs" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        target = backup_dir / f"{source.stem}_{timezone.now():%Y%m%d_%H%M%S}{source.suffix}"
        shutil.copy2(source, target)
        self._log(f"Database backup created: {target}")

    def _load_source(self, source):
        self._log(f"Reading {source['database']} ({source['language']})")
        data = {
            "source": source,
            "posts": {},
            "meta": defaultdict(dict),
            "terms": {},
            "taxonomies": {},
            "relationships": defaultdict(list),
            "comments": [],
            "users": {},
            "usermeta": defaultdict(dict),
            "options": {},
        }
        for table, row in iter_wordpress_rows(
            source["path"], source["prefix"], WANTED_TABLES
        ):
            if table == "posts":
                data["posts"][int(row["ID"])] = row
            elif table == "postmeta" and row.get("meta_key") in USEFUL_POSTMETA:
                data["meta"][int(row["post_id"])][row["meta_key"]] = row.get("meta_value") or ""
            elif table == "terms":
                data["terms"][int(row["term_id"])] = row
            elif table == "term_taxonomy":
                data["taxonomies"][int(row["term_taxonomy_id"])] = row
            elif table == "term_relationships":
                data["relationships"][int(row["object_id"])].append(int(row["term_taxonomy_id"]))
            elif table == "comments":
                data["comments"].append(row)
            elif table == "users":
                data["users"][int(row["ID"])] = row
            elif table == "usermeta" and row.get("meta_key") in USEFUL_USERMETA:
                data["usermeta"][int(row["user_id"])][row["meta_key"]] = row.get("meta_value") or ""
            elif table == "options" and row.get("option_name") in USEFUL_OPTIONS:
                data["options"][row["option_name"]] = row.get("option_value") or ""

        counts = Counter(post.get("post_type") for post in data["posts"].values())
        self._log(
            f"Parsed {counts['post']} posts, {counts['page']} pages, "
            f"{counts['attachment']} attachments, {len(data['comments'])} comments"
        )
        return data

    def _dry_run_report(self):
        for data in self.loaded_sources:
            language = data["source"]["language"]
            publishable = [
                row for row in data["posts"].values()
                if row.get("post_type") == "post" and row.get("post_status") in {"publish", "draft"}
            ]
            pages = [
                row for row in data["posts"].values()
                if row.get("post_type") == "page" and row.get("post_status") in {"publish", "draft"}
            ]
            approved = [
                row for row in data["comments"]
                if str(row.get("comment_approved")) == "1"
                and row.get("comment_type") in {"", "comment"}
                and not self._is_spam_comment(row)
            ]
            suspicious = [
                row for row in data["users"].values()
                if self._is_suspicious_user(row.get("user_login") or "")
            ]
            self._log(
                f"{language}: would process {len(publishable)} posts, {len(pages)} pages, "
                f"{len(approved)} approved comments, {len(data['users']) - len(suspicious)} trusted users, "
                f"{len(suspicious)} suspicious users skipped"
            )

    def _import_users(self, data):
        source = data["source"]
        User = get_user_model()
        for old_id, row in data["users"].items():
            login = (row.get("user_login") or "").strip()
            if self._is_suspicious_user(login):
                self.report["skipped_suspicious_users"] += 1
                self.warnings.append(f"Skipped suspicious user {source['database']}:{login}")
                continue
            source_record = self._source_record(source, "user", old_id)
            if source_record:
                user = source_record.content_object
            else:
                email = self._valid_email(row.get("user_email") or "")
                user = (
                    User.objects.exclude(wordpress_source="")
                    .filter(email__iexact=email)
                    .first()
                    if email
                    else None
                )
                display_name = self._fix_text(row.get("display_name") or "")
                if not user and display_name:
                    for candidate in User.objects.exclude(wordpress_source=""):
                        candidate_keys = {
                            self._person_key(candidate.username),
                            self._person_key(candidate.get_full_name()),
                        }
                        if self._person_key(display_name) in candidate_keys:
                            user = candidate
                            break
                if not user:
                    username = self._unique_username(
                        display_name or login or f"wp-user-{old_id}"
                    )
                    user = User(username=username)
                    user.set_unusable_password()
            meta = data["usermeta"].get(old_id, {})
            user.email = self._valid_email(row.get("user_email") or "") or user.email
            user.first_name = meta.get("first_name", "")[:150]
            user.last_name = meta.get("last_name", "")[:150]
            user.bio = meta.get("description", "")
            user.website = (row.get("user_url") or "")[:200]
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            user.wordpress_source = user.wordpress_source or source["database"]
            user.wordpress_user_id = user.wordpress_user_id or old_id
            user.imported_at = timezone.now()
            user.save()
            self.user_maps[(source["database"], old_id)] = user
            self._record_source(
                source, "user", old_id, user, row.get("user_url") or "", source_record
            )
            self.report[f"{source['language']}_authors"] += 1

    def _import_taxonomies(self, data):
        source = data["source"]
        language = source["language"]
        for taxonomy_id, taxonomy in data["taxonomies"].items():
            term = data["terms"].get(int(taxonomy["term_id"]))
            if not term:
                continue
            taxonomy_type = taxonomy.get("taxonomy")
            if taxonomy_type == "category":
                existing_source = self._source_record(source, "category", taxonomy_id)
                category = (
                    existing_source.content_object
                    if existing_source and existing_source.content_object
                    else self._match_or_create_category(term, taxonomy, language)
                )
                self._update_category_translation(category, term, taxonomy, language)
                self.category_maps[(source["database"], taxonomy_id)] = category
                self._record_source(
                    source,
                    "category",
                    taxonomy_id,
                    category,
                    f"{source['domain']}/category/{term.get('slug')}/",
                    self._source_record(source, "category", taxonomy_id),
                )
                self._create_redirect(
                    f"{source['domain']}/category/{term.get('slug')}/",
                    self._localized_url(category, language),
                    language,
                    "category",
                    taxonomy_id,
                )
                self.report["categories"] += 1
            elif taxonomy_type == "post_tag":
                existing_source = self._source_record(source, "tag", taxonomy_id)
                tag = (
                    existing_source.content_object
                    if existing_source and existing_source.content_object
                    else self._match_or_create_tag(term, language)
                )
                self._update_tag_translation(tag, term, language)
                self.tag_maps[(source["database"], taxonomy_id)] = tag
                self._record_source(
                    source,
                    "tag",
                    taxonomy_id,
                    tag,
                    f"{source['domain']}/tag/{term.get('slug')}/",
                    self._source_record(source, "tag", taxonomy_id),
                )
                self.report["tags"] += 1

    def _match_or_create_category(self, term, taxonomy, language):
        name = self._fix_text(term.get("name") or "")
        source_slug = slugify(term.get("slug") or name)
        normalized = self._normalize(name) or self._normalize(source_slug)
        canonical = next(
            (key for key, aliases in CATEGORY_ALIASES.items() if normalized in {self._normalize(a) for a in aliases}),
            None,
        )
        language_slug_field = f"slug_{language}"
        category = Category.objects.filter(
            Q(**{language_slug_field: source_slug})
            | Q(slug_en=source_slug)
            | Q(slug_fr=source_slug)
            | Q(slug_rw=source_slug)
        ).first()
        if not category and canonical:
            aliases = CATEGORY_ALIASES[canonical] | {canonical}
            for candidate in Category.objects.all():
                candidate_names = {
                    self._normalize(candidate.name_en or ""),
                    self._normalize(candidate.name_fr or ""),
                    self._normalize(candidate.name_rw or ""),
                }
                if candidate_names & {self._normalize(alias) for alias in aliases}:
                    category = candidate
                    break
        if not category:
            base_slug = canonical or self._unique_slug(Category, source_slug, "slug")
            category = Category(
                name=name,
                slug=base_slug,
                description=taxonomy.get("description") or "",
                is_active=True,
            )
        self._update_category_translation(category, term, taxonomy, language, canonical)
        return category

    def _update_category_translation(self, category, term, taxonomy, language, canonical=None):
        name = self._fix_text(term.get("name") or "")
        source_slug = slugify(term.get("slug") or name)
        if canonical is None:
            normalized = self._normalize(name) or self._normalize(source_slug)
            canonical = next(
                (
                    key
                    for key, aliases in CATEGORY_ALIASES.items()
                    if normalized in {self._normalize(alias) for alias in aliases}
                ),
                None,
            )
        setattr(category, f"name_{language}", name)
        translated_slug = canonical if language == "en" and canonical else source_slug
        current_owner = Category.objects.filter(**{f"slug_{language}": translated_slug}).exclude(pk=category.pk).first()
        if not current_owner:
            setattr(category, f"slug_{language}", translated_slug)
        setattr(category, f"description_{language}", taxonomy.get("description") or "")
        if language == "en" or not category.name_en:
            category.name_en = name
            if not category.slug_en:
                category.slug_en = canonical or source_slug
        category.save()

    def _match_or_create_tag(self, term, language):
        name = self._fix_text(term.get("name") or "")
        source_slug = slugify(term.get("slug") or name)
        tag = Tag.objects.filter(**{f"slug_{language}": source_slug}).first()
        if not tag:
            tag = Tag(name=name, slug=self._unique_slug(Tag, source_slug, "slug"))
        self._update_tag_translation(tag, term, language)
        return tag

    def _update_tag_translation(self, tag, term, language):
        name = self._fix_text(term.get("name") or "")
        source_slug = slugify(term.get("slug") or name)
        setattr(tag, f"name_{language}", name)
        current_owner = Tag.objects.filter(**{f"slug_{language}": source_slug}).exclude(pk=tag.pk).first()
        if not current_owner:
            setattr(tag, f"slug_{language}", source_slug)
        tag.save()

    def _import_media(self, data):
        source = data["source"]
        attachments = [
            row for row in data["posts"].values()
            if row.get("post_type") == "attachment"
        ]
        for row in attachments:
            old_id = int(row["ID"])
            meta = data["meta"].get(old_id, {})
            old_path = meta.get("_wp_attached_file", "")
            asset, _ = MediaAsset.objects.get_or_create(
                source_database=source["database"],
                old_wordpress_id=old_id,
                defaults={"source_language": source["language"]},
            )
            asset.title = self._fix_text(row.get("post_title") or "")
            asset.remote_url = row.get("guid") or (
                f"{source['domain']}/wp-content/uploads/{old_path}" if old_path else ""
            )
            asset.mime_type = row.get("post_mime_type") or ""
            asset.alt_text = self._fix_text(meta.get("_wp_attachment_image_alt", ""))
            asset.caption = self._fix_text(row.get("post_excerpt") or "")
            asset.description = self._clean_content(row.get("post_content") or "", source, {})
            asset.old_file_path = old_path
            asset.uploaded_at = self._parse_datetime(row.get("post_date"))

            media_root = source.get("media_root")
            local_path = media_root / Path(old_path) if media_root and old_path else None
            if local_path and local_path.exists() and local_path.is_file():
                destination_name = f"wordpress/{source['language']}/{old_path}".replace("\\", "/")
                if not asset.file or asset.file.name != destination_name:
                    with local_path.open("rb") as file_handle:
                        asset.file.save(destination_name, File(file_handle), save=False)
                asset.is_missing = False
            else:
                asset.is_missing = bool(old_path)
                if old_path:
                    self.report["missing_media"] += 1
            asset.save()
            self.media_maps[(source["database"], old_id)] = asset
            self.report["media"] += 1

    def _import_pages(self, data):
        source = data["source"]
        rows = [
            row for row in data["posts"].values()
            if row.get("post_type") == "page" and row.get("post_status") in {"publish", "draft"}
        ]
        if self.limit:
            rows = rows[:self.limit]
        for row in rows:
            old_id = int(row["ID"])
            existing_source = self._source_record(source, "page", old_id)
            page = existing_source.content_object if existing_source else self._match_page(row, source["language"])
            created = page is None
            if created:
                slug = self._unique_slug(Page, row.get("post_name") or f"page-{old_id}", "slug")
                page = Page(title=row.get("post_title") or slug, slug=slug, content="")
            language = source["language"]
            meta = data["meta"].get(old_id, {})
            clean_content = self._clean_content(row.get("post_content") or "", source, data)
            title = self._fix_text(row.get("post_title") or "")
            excerpt = self._fix_text(row.get("post_excerpt") or "")
            source_slug = slugify(row.get("post_name") or title)
            setattr(page, f"title_{language}", title)
            setattr(
                page,
                f"slug_{language}",
                self._safe_translated_slug(Page, language, source_slug, page, old_id),
            )
            setattr(page, f"content_{language}", clean_content)
            setattr(page, f"excerpt_{language}", excerpt)
            setattr(page, f"meta_title_{language}", self._seo_title(meta) or title)
            setattr(page, f"meta_description_{language}", self._seo_description(meta) or excerpt)
            if not page.title:
                page.title = title
            if not page.content:
                page.content = clean_content
            page.is_published = row.get("post_status") == "publish"
            page.is_active = True
            page.order = int(row.get("menu_order") or 0)
            self._assign_featured_image(page, meta, source)
            page.save()
            self.object_maps[(source["database"], "page", old_id)] = page
            old_url = self._old_url(row, source)
            self._record_source(source, "page", old_id, page, old_url, existing_source)
            self._create_redirect(
                old_url, self._localized_url(page, language), language, "page", old_id
            )
            self.report["pages"] += 1
            self.report[f"{language}_pages"] += 1

    def _import_posts(self, data):
        source = data["source"]
        rows = [
            row for row in data["posts"].values()
            if row.get("post_type") == "post" and row.get("post_status") in {"publish", "draft"}
        ]
        rows.sort(key=lambda row: row.get("post_date") or "")
        if self.limit:
            rows = rows[:self.limit]
        for row in rows:
            old_id = int(row["ID"])
            existing_source = self._source_record(source, "post", old_id)
            post = existing_source.content_object if existing_source else self._match_post(row, source["language"])
            if not post:
                base_slug = self._unique_slug(
                    Post, row.get("post_name") or f"post-{source['language']}-{old_id}", "slug"
                )
                post = Post(
                    title=self._fix_text(row.get("post_title") or base_slug),
                    slug=base_slug,
                    content="",
                )
            language = source["language"]
            meta = data["meta"].get(old_id, {})
            title = self._fix_text(row.get("post_title") or "")
            source_slug = slugify(row.get("post_name") or title)
            clean_content = self._clean_content(row.get("post_content") or "", source, data)
            excerpt = self._fix_text(row.get("post_excerpt") or "")
            setattr(post, f"title_{language}", title)
            setattr(
                post,
                f"slug_{language}",
                self._safe_translated_slug(Post, language, source_slug, post, old_id),
            )
            setattr(post, f"content_{language}", clean_content)
            setattr(post, f"excerpt_{language}", excerpt)
            setattr(post, f"seo_title_{language}", self._seo_title(meta))
            setattr(post, f"meta_description_{language}", self._seo_description(meta))
            if not post.title:
                post.title = title
            if not post.content:
                post.content = clean_content
            post.status = "published" if row.get("post_status") == "publish" else "draft"
            post.allow_comments = row.get("comment_status") == "open"
            post.views_count = max(post.views_count, self._views(meta))
            post.author = self.user_maps.get((source["database"], int(row.get("post_author") or 0)))
            post.published_at = self._parse_datetime(row.get("post_date"))
            self._assign_featured_image(post, meta, source)
            post.save()
            published_at = post.published_at
            updated_at = self._parse_datetime(row.get("post_modified"))
            Post.objects.filter(pk=post.pk).update(
                published_at=published_at,
                created_at=published_at or timezone.now(),
                updated_at=updated_at or timezone.now(),
            )
            self._assign_post_taxonomies(post, old_id, data)
            self.object_maps[(source["database"], "post", old_id)] = post
            old_url = self._old_url(row, source)
            self._record_source(source, "post", old_id, post, old_url, existing_source)
            self._create_redirect(
                old_url, self._localized_url(post, language), language, "post", old_id
            )
            self.report[f"{language}_posts"] += 1

    def _assign_post_taxonomies(self, post, old_id, data):
        source = data["source"]
        categories = []
        tags = []
        for taxonomy_id in data["relationships"].get(old_id, []):
            taxonomy = data["taxonomies"].get(taxonomy_id)
            if not taxonomy:
                continue
            if taxonomy.get("taxonomy") == "category":
                category = self.category_maps.get((source["database"], taxonomy_id))
                if category:
                    categories.append(category)
            elif taxonomy.get("taxonomy") == "post_tag":
                tag = self.tag_maps.get((source["database"], taxonomy_id))
                if tag:
                    tags.append(tag)
        if categories:
            post.category = categories[0]
            post.save(update_fields=["category"])
        if tags:
            post.tags.add(*tags)

    def _link_page_parents(self, data):
        source = data["source"]
        for row in data["posts"].values():
            if row.get("post_type") != "page":
                continue
            parent_id = int(row.get("post_parent") or 0)
            if not parent_id:
                continue
            page = self.object_maps.get((source["database"], "page", int(row["ID"])))
            parent = self.object_maps.get((source["database"], "page", parent_id))
            if page and parent and page.parent_id != parent.pk:
                page.parent = parent
                page.save(update_fields=["parent"])

    def _import_comments(self, data):
        source = data["source"]
        approved = [
            row for row in data["comments"]
            if str(row.get("comment_approved")) == "1"
            and (row.get("comment_type") or "comment") == "comment"
            and not self._is_spam_comment(row)
        ]
        for row in approved:
            old_id = int(row["comment_ID"])
            post = self.object_maps.get(
                (source["database"], "post", int(row.get("comment_post_ID") or 0))
            )
            if not post:
                self.report["skipped_comments"] += 1
                continue
            comment, _ = Comment.objects.update_or_create(
                source_database=source["database"],
                old_wordpress_id=old_id,
                defaults={
                    "post": post,
                    "author_name": self._fix_text(row.get("comment_author") or ""),
                    "author_email": self._valid_email(row.get("comment_author_email") or ""),
                    "content": self._fix_text(row.get("comment_content") or ""),
                    "status": "approved",
                    "source_language": source["language"],
                    "ip_address": self._valid_ip(row.get("comment_author_IP") or ""),
                },
            )
            created_at = self._parse_datetime(row.get("comment_date"))
            if created_at:
                Comment.objects.filter(pk=comment.pk).update(created_at=created_at)
            self.object_maps[(source["database"], "comment", old_id)] = comment
            self.report["comments"] += 1

        for row in approved:
            parent_id = int(row.get("comment_parent") or 0)
            if not parent_id:
                continue
            comment = self.object_maps.get(
                (source["database"], "comment", int(row["comment_ID"]))
            )
            parent = self.object_maps.get((source["database"], "comment", parent_id))
            if comment and parent and comment.parent_id != parent.pk:
                comment.parent = parent
                comment.save(update_fields=["parent"])

    def _import_books(self, data):
        source = data["source"]
        book_category, _ = BookCategory.objects.get_or_create(
            slug="imported-books", defaults={"name": "Imported Books"}
        )
        for row in data["posts"].values():
            if row.get("post_type") not in {"book", "books"}:
                continue
            old_id = int(row["ID"])
            title = self._fix_text(row.get("post_title") or f"Book {old_id}")
            slug = slugify(row.get("post_name") or title) or f"book-{old_id}"
            book, _ = Book.objects.update_or_create(
                slug=self._unique_slug(Book, slug, "slug", allow_existing_title=title),
                defaults={
                    "title": title,
                    "author": "Yves Gashugi",
                    "description": self._clean_content(row.get("post_content") or "", source, data),
                    "language": source["language"],
                    "category": book_category,
                    "published_at": (self._parse_datetime(row.get("post_date")) or timezone.now()).date(),
                    "is_active": row.get("post_status") == "publish",
                },
            )
            self._record_source(
                source,
                "book",
                old_id,
                book,
                self._old_url(row, source),
                self._source_record(source, "book", old_id),
            )
            self.report["books"] += 1

    def _import_site_settings(self):
        settings_obj = SiteSetting.objects.first() or SiteSetting(
            site_name="The Ransom Evangelistic Centre"
        )
        english = next(data for data in self.loaded_sources if data["source"]["language"] == "en")
        options = english["options"]
        settings_obj.site_name_en = self._fix_text(options.get("blogname") or settings_obj.site_name_en)
        settings_obj.tagline_en = self._fix_text(options.get("blogdescription") or settings_obj.tagline_en)
        email = self._valid_email(options.get("admin_email") or "")
        if email:
            settings_obj.email = email
            settings_obj.contact_email = email
        settings_obj.phone_1 = settings_obj.phone_1 or "+250 789 029 994"
        settings_obj.phone_2 = settings_obj.phone_2 or "+250 726 756 656"
        settings_obj.phone_3 = settings_obj.phone_3 or "+250 788 506 517"
        settings_obj.address_line_1_en = settings_obj.address_line_1_en or "Kinyinya, KG 12 Avenue"
        settings_obj.address_line_2_en = settings_obj.address_line_2_en or "Near Pottery Cafe Kigali"
        settings_obj.copyright_text_en = settings_obj.copyright_text_en or "©2024. Yves Gashugi. All Rights Reserved."
        settings_obj.save()

    def _match_page(self, row, language):
        source_slug = slugify(row.get("post_name") or "")
        canonical = next(
            (key for key, aliases in PAGE_ALIASES.items() if source_slug in aliases),
            None,
        )
        page = Page.objects.filter(**{f"slug_{language}": source_slug}).first()
        if not page and canonical:
            page = Page.objects.filter(slug_en=canonical).first()
        if not page:
            title = self._normalize(row.get("post_title") or "")
            best, best_score = None, 0
            for candidate in Page.objects.all():
                score = SequenceMatcher(
                    None, title, self._normalize(getattr(candidate, f"title_{language}") or candidate.title)
                ).ratio()
                if score > best_score:
                    best, best_score = candidate, score
            if best_score >= 0.92:
                page = best
        return page

    def _match_post(self, row, language):
        source_slug = slugify(row.get("post_name") or "")
        post = Post.objects.filter(**{f"slug_{language}": source_slug}).first()
        if post:
            return post
        title = self._normalize(row.get("post_title") or "")
        if not title:
            return None
        published = self._parse_datetime(row.get("post_date"))
        candidates = Post.objects.all()
        if published:
            candidates = candidates.filter(
                Q(published_at__isnull=True)
                | Q(published_at__range=(published - timedelta(days=7), published + timedelta(days=7)))
            )
        best, best_score = None, 0
        for candidate in candidates[:500]:
            candidate_title = self._normalize(
                getattr(candidate, f"title_{language}") or candidate.title_en or candidate.title
            )
            score = SequenceMatcher(None, title, candidate_title).ratio()
            if score > best_score:
                best, best_score = candidate, score
        return best if best_score >= 0.90 else None

    def _assign_featured_image(self, obj, meta, source):
        thumbnail_id = meta.get("_thumbnail_id")
        if not thumbnail_id:
            return
        try:
            thumbnail_id = int(thumbnail_id)
        except (TypeError, ValueError):
            return
        asset = self.media_maps.get((source["database"], thumbnail_id))
        if asset and asset.file:
            obj.featured_image.name = asset.file.name

    def _clean_content(self, content, source, data):
        content = self._fix_text(content or "")
        content = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
        content = re.sub(r"<style\b[^>]*>.*?</style>", "", content, flags=re.I | re.S)
        content = re.sub(r"<link\b[^>]*>", "", content, flags=re.I)
        content = re.sub(r"\[(?:/?)[A-Za-z][^\]]*\]", "", content)
        content = re.sub(r"<!--\s*/?wp:[\s\S]*?-->", "", content)
        content = re.sub(r"\s+class=(['\"])[^'\"]*\1", "", content)
        content = re.sub(r"\s+style=(['\"])[^'\"]*\1", "", content)

        for (database, _old_id), asset in self.media_maps.items():
            if database != source["database"] or not asset.file or not asset.old_file_path:
                continue
            old_url = f"{source['domain']}/wp-content/uploads/{asset.old_file_path}"
            content = content.replace(old_url, settings.MEDIA_URL + asset.file.name)

        content = bleach.clean(
            content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols={"http", "https", "mailto"},
            strip=True,
        )
        return content.strip()

    def _record_source(self, source, source_type, old_id, obj, old_url, existing=None):
        content_type = ContentType.objects.get_for_model(obj)
        defaults = {
            "source_language": source["language"],
            "old_url": old_url or "",
            "content_type": content_type,
            "object_id": obj.pk,
            "import_status": "updated" if existing else "imported",
        }
        ImportSource.objects.update_or_create(
            source_database=source["database"],
            source_type=source_type,
            old_wordpress_id=old_id,
            defaults=defaults,
        )

    def _source_record(self, source, source_type, old_id):
        return ImportSource.objects.filter(
            source_database=source["database"],
            source_type=source_type,
            old_wordpress_id=old_id,
        ).first()

    def _create_redirect(self, old_url, new_url, language, content_type, old_id):
        if not old_url or not old_url.startswith(("http://", "https://")):
            return
        Redirect.objects.update_or_create(
            old_url=old_url,
            defaults={
                "new_url": new_url,
                "source_language": language,
                "content_type_name": content_type,
                "old_object_id": old_id,
                "is_active": True,
            },
        )
        self.report["redirects"] += 1

    def _localized_url(self, obj, language):
        with translation.override(language):
            return obj.get_absolute_url()

    def _old_url(self, row, source):
        guid = row.get("guid") or ""
        if guid.startswith(("http://", "https://")) and "?" not in guid:
            return guid
        slug = row.get("post_name") or ""
        post_type = row.get("post_type")
        if post_type == "page":
            return f"{source['domain']}/{slug}/"
        published = self._parse_datetime(row.get("post_date"))
        if published:
            return f"{source['domain']}/{published:%Y/%m/%d}/{slug}/"
        return f"{source['domain']}/{slug}/"

    def _seo_title(self, meta):
        return self._fix_text(meta.get("_yoast_wpseo_title") or meta.get("rank_math_title") or "")[:200]

    def _seo_description(self, meta):
        return self._fix_text(
            meta.get("_yoast_wpseo_metadesc") or meta.get("rank_math_description") or ""
        )

    def _views(self, meta):
        for key in ("post_views_count", "_post_views_count", "views", "entry_views"):
            try:
                return max(0, int(float(meta.get(key) or 0)))
            except (TypeError, ValueError):
                continue
        return 0

    def _parse_datetime(self, value):
        if not value or value == "0000-00-00 00:00:00":
            return None
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        except (TypeError, ValueError):
            return None

    def _fix_text(self, value):
        value = str(value or "").replace("\x00", "")
        try:
            if any(marker in value for marker in ("â€™", "Ã", "ðŸ")):
                value = value.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        return value.strip()

    def _normalize(self, value):
        value = strip_tags(self._fix_text(value)).lower()
        return re.sub(r"[^a-z0-9\u00c0-\u024f]+", " ", value).strip()

    def _person_key(self, value):
        return " ".join(sorted(self._normalize(value).split()))

    def _valid_email(self, value):
        value = (value or "").strip().lower()
        if not value:
            return ""
        try:
            validate_email(value)
            return value
        except ValidationError:
            return ""

    def _valid_ip(self, value):
        value = (value or "").strip()
        return value if re.fullmatch(r"[0-9a-fA-F:.]+", value) else None

    def _is_suspicious_user(self, username):
        return not username or bool(SUSPICIOUS_USERNAME_RE.search(username))

    def _is_spam_comment(self, row):
        content = (row.get("comment_content") or "").lower()
        author = (row.get("comment_author") or "").lower()
        author_url = (row.get("comment_author_url") or "").lower()
        if len(content) > 5000:
            return True
        if len(re.findall(r"https?://|www\.", content)) > 2:
            return True
        spam_markers = (
            "call girls",
            "escorts",
            "payday loan",
            "casino",
            "porn",
            "sex video",
            "viagra",
            "backlink",
            "crypto investment",
            "online pharmacy",
            "telegram",
            "whatsapp group",
        )
        if any(marker in content or marker in author or marker in author_url for marker in spam_markers):
            return True
        if author_url and not any(
            trusted in author_url
            for trusted in ("yvesgashugi.org", "gashugiyves.org", "facebook.com", "youtube.com")
        ):
            return True
        return False

    def _unique_username(self, value):
        User = get_user_model()
        base = slugify(value)[:140] or "imported-author"
        candidate, counter = base, 2
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base}-{counter}"[:150]
            counter += 1
        return candidate

    def _unique_slug(self, model, value, field, allow_existing_title=None):
        base = slugify(value)[:500] or "imported-item"
        candidate, counter = base, 2
        while self._slug_exists(model, field, candidate):
            if allow_existing_title:
                existing = model.objects.filter(**{field: candidate}).first()
                if existing and getattr(existing, "title", None) == allow_existing_title:
                    return candidate
            candidate = f"{base}-{counter}"[:500]
            counter += 1
        return candidate

    def _slug_exists(self, model, field, candidate):
        manager = model.objects
        if hasattr(manager, "rewrite"):
            try:
                if manager.rewrite(False).filter(**{field: candidate}).exists():
                    return True
            except Exception:
                pass
        query = Q(**{field: candidate})
        for language in ("en", "fr", "rw"):
            translated_field = f"{field}_{language}"
            if any(item.name == translated_field for item in model._meta.fields):
                query |= Q(**{translated_field: candidate})
        return manager.filter(query).exists()

    def _safe_translated_slug(self, model, language, candidate, obj, old_id):
        field = f"slug_{language}"
        owner = model.objects.filter(**{field: candidate}).exclude(pk=obj.pk).first()
        if not owner:
            return candidate
        base = f"{candidate}-{old_id}"[:500]
        unique = base
        counter = 2
        while model.objects.filter(**{field: unique}).exclude(pk=obj.pk).exists():
            unique = f"{base}-{counter}"[:500]
            counter += 1
        self.warnings.append(
            f"Duplicate {language} slug '{candidate}' normalized to '{unique}'"
        )
        return unique

    def _reset_previous_imports(self):
        self._log("Resetting previously imported WordPress records", self.style.WARNING)
        Comment.objects.exclude(old_wordpress_id__isnull=True).delete()
        MediaAsset.objects.all().delete()
        Redirect.objects.exclude(old_object_id__isnull=True).delete()
        sources = list(ImportSource.objects.select_related("content_type"))
        protected_models = {Page, Category, Book}
        objects = {}
        for source in sources:
            objects[(source.content_type_id, source.object_id)] = source.content_object
        for obj in objects.values():
            if not obj or obj.__class__ in protected_models:
                continue
            if obj.__class__ is get_user_model() and not obj.wordpress_source:
                continue
            obj.delete()
        ImportSource.objects.all().delete()

    def _finish(self):
        if not self.dry_run:
            self.report["redirects"] = Redirect.objects.exclude(old_object_id__isnull=True).count()
        self.report["warnings"] = len(self.warnings)
        self.report["errors"] = len(self.errors)
        lines = [
            "",
            "WordPress import report",
            f"English posts imported: {self.report['en_posts']}",
            f"French posts imported: {self.report['fr_posts']}",
            f"Kinyarwanda posts imported: {self.report['rw_posts']}",
            f"Pages imported/updated: {self.report['pages']}",
            f"Categories processed: {self.report['categories']}",
            f"Tags processed: {self.report['tags']}",
            f"Approved comments imported: {self.report['comments']}",
            f"Media records imported: {self.report['media']}",
            f"Missing media files: {self.report['missing_media']}",
            f"Redirects created: {self.report['redirects']}",
            f"Suspicious users skipped: {self.report['skipped_suspicious_users']}",
            f"Books imported: {self.report['books']}",
            f"Warnings: {self.report['warnings']}",
            f"Errors: {self.report['errors']}",
            f"Log file: {self.log_path}",
        ]
        for line in lines:
            self.stdout.write(line)
            logging.info(line)
        if self.warnings:
            logging.warning("\n".join(self.warnings))
        if self.errors:
            logging.error("\n".join(self.errors))
        self.stdout.write(self.style.SUCCESS("WordPress import completed."))
