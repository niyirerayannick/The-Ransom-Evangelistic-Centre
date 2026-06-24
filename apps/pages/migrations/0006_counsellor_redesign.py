from django.db import migrations, models
import ckeditor.fields


def migrate_counselling_types(apps, schema_editor):
    CounsellingRequest = apps.get_model("pages", "CounsellingRequest")
    CounsellingRequest.objects.filter(counselling_type="leadership").update(counselling_type="general")


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0005_donation_redesign"),
    ]

    operations = [
        migrations.CreateModel(
            name="Counsellor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("name_en", models.CharField(max_length=200, null=True)),
                ("name_fr", models.CharField(max_length=200, null=True)),
                ("name_rw", models.CharField(max_length=200, null=True)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("role", models.CharField(max_length=250)),
                ("role_en", models.CharField(max_length=250, null=True)),
                ("role_fr", models.CharField(max_length=250, null=True)),
                ("role_rw", models.CharField(max_length=250, null=True)),
                ("photo", models.ImageField(blank=True, upload_to="counsellors/")),
                ("external_photo_url", models.URLField(blank=True)),
                ("bio", ckeditor.fields.RichTextField(blank=True)),
                ("bio_en", ckeditor.fields.RichTextField(blank=True, null=True)),
                ("bio_fr", ckeditor.fields.RichTextField(blank=True, null=True)),
                ("bio_rw", ckeditor.fields.RichTextField(blank=True, null=True)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("seed_key", models.SlugField(blank=True, max_length=80, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Counsellor",
                "verbose_name_plural": "Counsellors",
                "ordering": ["order", "name"],
            },
        ),
        migrations.AddField(
            model_name="counsellingrequest",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="counsellingrequest",
            name="counselling_type",
            field=models.CharField(
                choices=[
                    ("trauma", "Trauma support"),
                    ("spiritual", "Spiritual counselling"),
                    ("family", "Family counselling"),
                    ("healing", "Healing support"),
                    ("general", "General support"),
                ],
                max_length=30,
            ),
        ),
        migrations.RunPython(migrate_counselling_types, migrations.RunPython.noop),
    ]
