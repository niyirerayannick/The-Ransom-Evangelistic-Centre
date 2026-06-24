from django.contrib import admin
from .models import Subscriber, NewsletterCampaign


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "subscribed_at"]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["email", "name"]


class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ["subject", "sent_at", "created_at"]
    list_filter = ["sent_at"]


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(NewsletterCampaign, NewsletterCampaignAdmin)
