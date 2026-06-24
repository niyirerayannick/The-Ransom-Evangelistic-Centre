from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_imported_at_user_wordpress_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language_preference",
            field=models.CharField(
                blank=True,
                choices=[("en", "English"), ("fr", "French"), ("rw", "Kinyarwanda")],
                default="en",
                max_length=5,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super Admin"),
                    ("admin", "Admin"),
                    ("editor", "Editor"),
                    ("author", "Author"),
                    ("viewer", "Viewer"),
                ],
                default="author",
                max_length=20,
            ),
        ),
    ]
