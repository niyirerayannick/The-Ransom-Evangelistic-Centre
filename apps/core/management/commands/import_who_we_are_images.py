from django.core.management.base import BaseCommand

from apps.core.who_we_are_images import import_who_we_are_images


class Command(BaseCommand):
    help = "Assign about-section photos from existing ministry media (leadership, counsellor, or local files)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace images even when one is already set.",
        )

    def handle(self, *args, **options):
        results, homepage_source, page_source = import_who_we_are_images(force=options["force"])

        if results["homepage"]:
            self.stdout.write(self.style.SUCCESS(
                f"Homepage Who we are image set from {homepage_source}"
            ))
        elif homepage_source:
            self.stdout.write("Homepage Who we are image already set (use --force to replace).")
        else:
            self.stdout.write(self.style.WARNING("No suitable homepage image source found."))

        if results["page"]:
            self.stdout.write(self.style.SUCCESS(
                f"Who we are page featured image set from {page_source}"
            ))
        elif page_source:
            self.stdout.write("Who we are page image already set (use --force to replace).")
        else:
            self.stdout.write(self.style.WARNING("No suitable Who we are page image source found."))
