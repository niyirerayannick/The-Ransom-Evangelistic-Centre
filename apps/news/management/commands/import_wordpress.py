"""
Management command to import WordPress content from a MySQL database.

Usage:
    python manage.py import_wordpress --db-name=wordpress_db --db-user=root --db-password=pass --db-host=localhost

Maps WordPress tables (wp_posts, wp_postmeta, wp_terms, wp_term_taxonomy, wp_term_relationships)
into clean Django models (Post, Category, Tag, Page).

Preserves original slugs, dates, and imports featured images.
"""

import os
import re
import shutil
from datetime import datetime
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.conf import settings
from django.db import transaction

import MySQLdb


class Command(BaseCommand):
    help = "Import content from WordPress MySQL database into Django models"

    def add_arguments(self, parser):
        parser.add_argument("--db-name", required=True, help="WordPress MySQL database name")
        parser.add_argument("--db-user", default="root", help="MySQL user")
        parser.add_argument("--db-password", default="", help="MySQL password")
        parser.add_argument("--db-host", default="localhost", help="MySQL host")
        parser.add_argument("--db-port", default=3306, type=int, help="MySQL port")
        parser.add_argument("--table-prefix", default="wp_", help="WordPress table prefix")
        parser.add_argument("--uploads-dir", default="", help="Path to wp-content/uploads directory for image migration")
        parser.add_argument("--media-dest", default="", help="Destination media directory (default: MEDIA_ROOT/posts/)")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be imported without importing")

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.table_prefix = options["table_prefix"]
        self.uploads_dir = options["uploads_dir"]
        self.media_dest = options.get("media_dest") or os.path.join(settings.MEDIA_ROOT, "posts")

        self._connect_db(options)
        self._import_categories()
        self._import_tags()
        self._import_posts_and_pages()
        self._close_db()
        self.stdout.write(self.style.SUCCESS("WordPress import completed successfully."))

    def _connect_db(self, options):
        self.stdout.write("Connecting to MySQL database...")
        try:
            self.conn = MySQLdb.connect(
                host=options["db_host"],
                port=options["db_port"],
                user=options["db_user"],
                passwd=options["db_password"],
                db=options["db_name"],
                charset="utf8mb4",
                use_unicode=True,
            )
            self.cursor = self.conn.cursor()
            self.stdout.write(self.style.SUCCESS("Connected to MySQL."))
        except Exception as e:
            raise CommandError(f"Failed to connect to MySQL: {e}")

    def _close_db(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def _fetch_all(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def _fetch_one(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def _import_categories(self):
        self.stdout.write("Importing categories...")
        wp_term_taxonomy = f"{self.table_prefix}term_taxonomy"
        wp_terms = f"{self.table_prefix}terms"
        wp_termmeta = f"{self.table_prefix}termmeta"

        rows = self._fetch_all(f"""
            SELECT t.term_id, t.name, t.slug, tt.description, tt.parent, tt.term_taxonomy_id
            FROM {wp_terms} t
            JOIN {wp_term_taxonomy} tt ON t.term_id = tt.term_id
            WHERE tt.taxonomy = 'category'
        """)

        from apps.news.models import Category

        for term_id, name, slug, description, parent_id, tt_id in rows:
            if self.dry_run:
                self.stdout.write(f"  [DRY RUN] Would import category: {name} (slug: {slug})")
                continue

            cat, created = Category.objects.get_or_create(
                slug=slug or slugify(name, allow_unicode=True),
                defaults={
                    "name": name,
                    "description": description or "",
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"  Imported category: {name}")

            wp_term_map = getattr(self, "_wp_term_map", {})
            wp_term_map[term_id] = cat
            self._wp_term_map = wp_term_map

    def _import_tags(self):
        self.stdout.write("Importing tags...")
        wp_terms = f"{self.table_prefix}terms"
        wp_term_taxonomy = f"{self.table_prefix}term_taxonomy"

        rows = self._fetch_all(f"""
            SELECT t.term_id, t.name, t.slug
            FROM {wp_terms} t
            JOIN {wp_term_taxonomy} tt ON t.term_id = tt.term_id
            WHERE tt.taxonomy = 'post_tag'
        """)

        from apps.news.models import Tag

        for term_id, name, slug in rows:
            if self.dry_run:
                self.stdout.write(f"  [DRY RUN] Would import tag: {name}")
                continue

            tag, created = Tag.objects.get_or_create(
                slug=slug or slugify(name, allow_unicode=True),
                defaults={"name": name},
            )
            if created:
                self.stdout.write(f"  Imported tag: {name}")

            wp_tag_map = getattr(self, "_wp_tag_map", {})
            wp_tag_map[term_id] = tag
            self._wp_tag_map = wp_tag_map

    def _import_posts_and_pages(self):
        self.stdout.write("Importing posts and pages...")
        wp_posts = f"{self.table_prefix}posts"
        wp_postmeta = f"{self.table_prefix}postmeta"
        wp_term_relationships = f"{self.table_prefix}term_relationships"

        rows = self._fetch_all(f"""
            SELECT ID, post_title, post_name, post_content, post_excerpt,
                   post_status, post_date, post_modified, post_type, post_author,
                   post_password, menu_order
            FROM {wp_posts}
            WHERE post_type IN ('post', 'page')
              AND post_status IN ('publish', 'draft')
            ORDER BY post_date ASC
        """)

        from apps.news.models import Post, Category, Tag
        from apps.pages.models import Page

        post_category_map = {}
        post_tag_map = {}

        for row in rows:
            (post_id, title, slug, content, excerpt, status, post_date,
             post_modified, post_type, post_author, post_password, menu_order) = row

            if not title or not slug:
                continue

            is_published = status == "publish"
            published_at = post_date if is_published else None

            # Get featured image from wp_postmeta
            featured_url = self._fetch_one(f"""
                SELECT meta_value FROM {wp_postmeta}
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
            """, (post_id,))

            featured_image_path = None
            if featured_url:
                thumbnail_id = featured_url[0]
                featured_path = self._fetch_one(f"""
                    SELECT meta_value FROM {wp_postmeta}
                    WHERE post_id = %s AND meta_key = '_wp_attached_file'
                """, (thumbnail_id,))
                if featured_path:
                    featured_image_path = self._migrate_image(featured_path[0])

            # Get categories for this post
            cat_rows = self._fetch_all(f"""
                SELECT tt.term_id FROM {wp_term_relationships} tr
                JOIN {wp_term_taxonomy} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
                WHERE tr.object_id = %s AND tt.taxonomy = 'category'
            """, (post_id,))

            # Get tags for this post
            tag_rows = self._fetch_all(f"""
                SELECT tt.term_id FROM {wp_term_relationships} tr
                JOIN {wp_term_taxonomy} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
                WHERE tr.object_id = %s AND tt.taxonomy = 'post_tag'
            """, (post_id,))

            # Get SEO meta
            seo_title = self._fetch_one(f"""
                SELECT meta_value FROM {wp_postmeta}
                WHERE post_id = %s AND meta_key = '_yoast_wpseo_title'
            """, (post_id,))
            seo_title = seo_title[0] if seo_title else ""

            meta_desc = self._fetch_one(f"""
                SELECT meta_value FROM {wp_postmeta}
                WHERE post_id = %s AND meta_key = '_yoast_wpseo_metadesc'
            """, (post_id,))
            meta_desc = meta_desc[0] if meta_desc else ""

            if self.dry_run:
                self.stdout.write(f"  [DRY RUN] Would import {post_type}: {title} (slug: {slug})")
                continue

            # Clean content - fix WordPress URLs
            content = self._fix_wordpress_urls(content)

            if post_type == "page":
                page, created = Page.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "content": content,
                        "is_published": is_published,
                        "order": menu_order or 0,
                        "seo_title": seo_title,
                        "meta_description": meta_desc,
                        "created_at": post_date,
                        "updated_at": post_modified,
                    },
                )
                if not created:
                    page.title = title
                    page.content = content
                    page.is_published = is_published
                    page.save()

                self.stdout.write(f"  Imported page: {title}")
                self._create_redirect(post_id, f"/{slug}/")

            else:
                post, created = Post.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "slug": slug,
                        "content": content,
                        "excerpt": excerpt or "",
                        "status": "published" if is_published else "draft",
                        "published_at": published_at,
                        "seo_title": seo_title,
                        "meta_description": meta_desc,
                        "created_at": post_date,
                        "updated_at": post_modified,
                        "is_featured": False,
                        "is_breaking": False,
                        "allow_comments": True,
                    },
                )

                if not created:
                    post.title = title
                    post.content = content
                    post.excerpt = excerpt or ""
                    post.status = "published" if is_published else "draft"
                    if published_at:
                        post.published_at = published_at
                    post.seo_title = seo_title
                    post.meta_description = meta_desc
                    post.save()

                # Assign categories
                if cat_rows:
                    wp_term_map = getattr(self, "_wp_term_map", {})
                    for (term_id,) in cat_rows:
                        if term_id in wp_term_map:
                            post.category = wp_term_map[term_id]
                            post.save()

                # Assign tags
                if tag_rows:
                    wp_tag_map = getattr(self, "_wp_tag_map", {})
                    for (term_id,) in tag_rows:
                        if term_id in wp_tag_map:
                            post.tags.add(wp_tag_map[term_id])

                self.stdout.write(f"  Imported post: {title}")

    def _migrate_image(self, relative_path):
        """Migrate image from wp-content/uploads to Django media directory."""
        if not self.uploads_dir:
            return None

        source = os.path.join(self.uploads_dir, relative_path)
        if not os.path.exists(source):
            self.stdout.write(self.style.WARNING(f"    Image not found: {source}"))
            return None

        dest_dir = os.path.join(self.media_dest, os.path.dirname(relative_path))
        os.makedirs(dest_dir, exist_ok=True)

        filename = os.path.basename(relative_path)
        dest = os.path.join(dest_dir, filename)

        try:
            shutil.copy2(source, dest)
            rel_dest = os.path.join("posts", relative_path).replace("\\", "/")
            self.stdout.write(f"    Migrated image: {rel_dest}")
            return rel_dest
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    Failed to migrate image {source}: {e}"))
            return None

    def _fix_wordpress_urls(self, content):
        """Replace old WordPress URLs with new Django URLs."""
        if not content:
            return content

        # Replace old site URL references
        content = content.replace("https://yvesgashugi.org/wp-content/uploads", settings.MEDIA_URL.rstrip("/") + "/uploads")
        content = content.replace("http://yvesgashugi.org/wp-content/uploads", settings.MEDIA_URL.rstrip("/") + "/uploads")

        return content

    def _create_redirect(self, old_post_id, new_path):
        """Store redirect mapping from old WordPress post ID to new URL path.
        
        This creates a simple redirect mechanism by storing in SiteSetting or a
        dedicated Redirect model. For now, logs the redirect for nginx/apache use.
        """
        old_url = f"/?p={old_post_id}"
        self.stdout.write(f"    Redirect: {old_url} -> {new_path}")
