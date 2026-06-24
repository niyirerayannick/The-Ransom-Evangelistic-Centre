from django.core.management.base import BaseCommand

from apps.news.homepage import demo_post_q
from apps.news.models import Post


class Command(BaseCommand):
    help = "Remove seed/demo/sample posts without touching imported WordPress or author content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List demo posts that would be removed without deleting them.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        demo_posts = Post.objects.filter(demo_post_q()).order_by("pk")
        count = demo_posts.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No demo posts found."))
            return

        if dry_run:
            self.stdout.write(f"Would remove {count} demo post(s):\n")
            for post in demo_posts:
                self.stdout.write(f"  - [{post.pk}] {post.title}")
            return

        deleted, _ = demo_posts.delete()
        self.stdout.write(self.style.SUCCESS(f"Removed {deleted} demo post record(s)."))
        self.stdout.write(
            f"Remaining posts: {Post.objects.count()} "
            f"({Post.objects.filter(status='published').count()} published)"
        )
