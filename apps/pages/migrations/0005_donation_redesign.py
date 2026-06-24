from django.db import migrations, models


PURPOSE_MAP = {
    "publications": "articles_writing",
    "counselling": "healing_activities",
    "outreach": "healing_activities",
    "general": "both",
    "books": "both",
}

STATUS_MAP = {
    "received": "completed",
}


def migrate_pledge_fields(apps, schema_editor):
    DonationPledge = apps.get_model("pages", "DonationPledge")
    for pledge in DonationPledge.objects.all():
        old_purpose = getattr(pledge, "donation_purpose", None)
        if old_purpose:
            pledge.program_to_donate = PURPOSE_MAP.get(old_purpose, "both")
        if not pledge.telephone:
            pledge.telephone = getattr(pledge, "phone", "") or ""
        if not pledge.feedback:
            pledge.feedback = getattr(pledge, "message", "") or ""
        if not pledge.donation_commitment:
            pledge.donation_commitment = "one_time"
        if not pledge.payment_gateway:
            pledge.payment_gateway = "bank_transfer"
        if pledge.status in STATUS_MAP:
            pledge.status = STATUS_MAP[pledge.status]
        pledge.save()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0004_leadership_member_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="DonationProgram",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("title_en", models.CharField(max_length=200, null=True)),
                ("title_fr", models.CharField(max_length=200, null=True)),
                ("title_rw", models.CharField(max_length=200, null=True)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                ("description_en", models.TextField(blank=True, null=True)),
                ("description_fr", models.TextField(blank=True, null=True)),
                ("description_rw", models.TextField(blank=True, null=True)),
                ("icon", models.CharField(blank=True, max_length=20)),
                ("image", models.ImageField(blank=True, upload_to="donations/programs/")),
                ("order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["order", "title"],
            },
        ),
        migrations.AddField(
            model_name="donationmethod",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="donationmethod",
            name="currency",
            field=models.CharField(blank=True, default="RWF", max_length=10),
        ),
        migrations.AddField(
            model_name="donationmethod",
            name="icon",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="donationmethod",
            name="seed_key",
            field=models.SlugField(blank=True, max_length=80, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="donationmethod",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="donationmethod",
            name="mobile_money_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="donation_commitment",
            field=models.CharField(
                choices=[
                    ("one_time", "One time"),
                    ("monthly", "Monthly"),
                    ("quarterly", "Quarterly"),
                    ("annually", "Annually"),
                ],
                default="one_time",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="feedback",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="payment_gateway",
            field=models.CharField(
                choices=[
                    ("cash", "Cash"),
                    ("mobile_money", "Mobile Money"),
                    ("bank_transfer", "Bank Transfer"),
                ],
                default="bank_transfer",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="program_to_donate",
            field=models.CharField(
                choices=[
                    ("articles_writing", "Articles Writing"),
                    ("healing_activities", "Healing activities"),
                    ("both", "Both"),
                ],
                default="both",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="telephone",
            field=models.CharField(default="", max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="donationpledge",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name="donationpledge",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="donationpledge",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("contacted", "Contacted"),
                    ("confirmed", "Confirmed"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="new",
                max_length=20,
            ),
        ),
        migrations.RunPython(migrate_pledge_fields, migrations.RunPython.noop),
        migrations.RemoveField(model_name="donationpledge", name="donation_purpose"),
        migrations.RemoveField(model_name="donationpledge", name="message"),
        migrations.RemoveField(model_name="donationpledge", name="phone"),
    ]
