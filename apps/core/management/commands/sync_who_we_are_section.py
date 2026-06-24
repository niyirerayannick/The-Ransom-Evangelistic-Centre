from django.core.management.base import BaseCommand

from apps.core.homepage_content import sync_who_we_are_section


class Command(BaseCommand):
    help = "Sync multilingual copy for the homepage Who we are section (EN/FR/RW)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing translated fields with defaults.",
        )

    def handle(self, *args, **options):
        section = sync_who_we_are_section(force=options["force"])
        self.stdout.write(self.style.SUCCESS(f"Synced homepage section: {section.key} (pk={section.pk})"))
