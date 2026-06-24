from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from apps.core.models import ImportSource
from apps.news.models import Post
from apps.news.homepage import (
    post_has_language_content,
    post_available_in_language_q,
    strip_html,
    LANGUAGE_CODES,
)


class Command(BaseCommand):
    help = "Audit post language coverage and optionally fix source_language values."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix-source-language",
            action="store_true",
            help="Set source_language on posts based on populated translated fields and import records.",
        )

    def handle(self, *args, **options):
        posts = Post.objects.all()
        total = posts.count()
        self.stdout.write(f"Total posts: {total}")

        for lang in LANGUAGE_CODES:
            count = posts.filter(post_available_in_language_q(lang)).count()
            self.stdout.write(f"{lang} available: {count}")

        missing = {lang: 0 for lang in LANGUAGE_CODES}
        no_language = 0
        missing_source = Post.objects.filter(Q(source_language="") | Q(source_language__isnull=True)).count()

        published = Post.objects.filter(status=Post.STATUS_PUBLISHED)
        for lang in LANGUAGE_CODES:
            missing[lang] = published.exclude(post_available_in_language_q(lang)).count()

        for post in posts.iterator():
            if not any(post_has_language_content(post, lang) for lang in LANGUAGE_CODES):
                no_language += 1

        self.stdout.write(f"Missing English content: {missing['en']}")
        self.stdout.write(f"Missing French content: {missing['fr']}")
        self.stdout.write(f"Missing Kinyarwanda content: {missing['rw']}")
        self.stdout.write(f"Posts with no language content: {no_language}")
        self.stdout.write(f"Posts with source_language missing: {missing_source}")

        if options["fix_source_language"]:
            updated = self._fix_source_languages(posts)
            self.stdout.write(self.style.SUCCESS(f"Updated source_language on {updated} post(s)."))

    def _fix_source_languages(self, posts):
        content_type = ContentType.objects.get_for_model(Post)
        updated = 0
        for post in posts.iterator():
            available = [lang for lang in LANGUAGE_CODES if post_has_language_content(post, lang)]
            source_langs = list(
                ImportSource.objects.filter(content_type=content_type, object_id=post.pk)
                .values_list("source_language", flat=True)
                .distinct()
            )
            new_value = ""
            if len(available) == 1:
                new_value = available[0]
            elif len(source_langs) == 1:
                new_value = source_langs[0]
            elif "en" in available:
                new_value = "en"
            elif available:
                new_value = available[0]

            if post.source_language != new_value:
                post.source_language = new_value
                post.save(update_fields=["source_language", "updated_at"])
                updated += 1
        return updated
