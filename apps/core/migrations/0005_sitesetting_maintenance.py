from django.db import migrations, models

from apps.core.maintenance import DEFAULT_MAINTENANCE_COPY


def seed_maintenance_defaults(apps, schema_editor):
    SiteSetting = apps.get_model("core", "SiteSetting")
    for setting in SiteSetting.objects.all():
        changed = False
        for lang, copy in DEFAULT_MAINTENANCE_COPY.items():
            title_field = f"maintenance_title_{lang}"
            message_field = f"maintenance_message_{lang}"
            if not getattr(setting, title_field, None):
                setattr(setting, title_field, copy["title"])
                changed = True
            if not getattr(setting, message_field, None):
                setattr(setting, message_field, copy["message"])
                changed = True
        if not setting.maintenance_title:
            setting.maintenance_title = DEFAULT_MAINTENANCE_COPY["en"]["title"]
            changed = True
        if not setting.maintenance_message:
            setting.maintenance_message = DEFAULT_MAINTENANCE_COPY["en"]["message"]
            changed = True
        if changed:
            setting.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_redirect_mediaasset_importsource"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_contact_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_expected_launch_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_message",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_message_en",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_message_fr",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_message_rw",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_mode",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_show_countdown",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_title_en",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_title_fr",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="maintenance_title_rw",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.RunPython(seed_maintenance_defaults, migrations.RunPython.noop),
    ]
