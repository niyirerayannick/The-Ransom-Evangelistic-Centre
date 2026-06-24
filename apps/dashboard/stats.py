"""Real database statistics for the dashboard."""

from django.db.models import Count, Q

from apps.accounts.models import User
from apps.comments.models import Comment
from apps.core.models import Advertisement, HomepageSection, MenuItem, Partner, SiteSetting
from apps.news.models import Post, Category, Tag, MediaLibrary
from apps.news.homepage import post_available_in_language_q
from apps.newsletter.models import Subscriber
from apps.pages.models import (
    Page, Book, CounsellingRequest, ContactMessage, DonationPledge,
)


def _post_scope(user):
    qs = Post.objects.all()
    role = user.role if not user.is_superuser else "super_admin"
    if user.is_superuser or role in ("super_admin", "admin", "editor", "viewer"):
        return qs
    return qs.filter(author=user)


def dashboard_stats(user):
    posts = _post_scope(user)
    return {
        "total_posts": posts.count(),
        "published_posts": posts.filter(status=Post.STATUS_PUBLISHED).count(),
        "draft_posts": posts.filter(status=Post.STATUS_DRAFT).count(),
        "pending_review_posts": posts.filter(status=Post.STATUS_PENDING_REVIEW).count(),
        "rejected_posts": posts.filter(status=Post.STATUS_REJECTED).count(),
        "posts_en": posts.filter(post_available_in_language_q("en")).count(),
        "posts_fr": posts.filter(post_available_in_language_q("fr")).count(),
        "posts_rw": posts.filter(post_available_in_language_q("rw")).count(),
        "total_pages": Page.objects.count(),
        "published_pages": Page.objects.filter(is_published=True).count(),
        "total_categories": Category.objects.count(),
        "total_tags": Tag.objects.count(),
        "total_media": MediaLibrary.objects.count(),
        "pending_comments": Comment.objects.filter(status="pending").count(),
        "total_comments": Comment.objects.count(),
        "counselling_new": CounsellingRequest.objects.filter(status="new").count(),
        "total_counselling": CounsellingRequest.objects.count(),
        "contact_new": ContactMessage.objects.filter(status="new").count(),
        "total_contact": ContactMessage.objects.count(),
        "donations_new": DonationPledge.objects.filter(status="new").count(),
        "total_donations": DonationPledge.objects.count(),
        "total_books": Book.objects.count(),
        "total_subscribers": Subscriber.objects.filter(is_active=True).count(),
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "total_ads": Advertisement.objects.count(),
        "total_partners": Partner.objects.filter(is_active=True).count(),
        "total_menus": MenuItem.objects.filter(parent__isnull=True).count(),
        "homepage_sections": HomepageSection.objects.filter(is_active=True).count(),
        "has_settings": SiteSetting.objects.exists(),
    }


def module_cards(user):
    from .roles import user_can_access_module

    stats = dashboard_stats(user)
    cards = [
        ("posts", "Posts", "Create and manage multilingual articles", stats["total_posts"], "dashboard:post_list", "article"),
        ("pages", "Pages", "Manage institutional and ministry pages", stats["total_pages"], "dashboard:page_list", "description"),
        ("categories", "Categories", "Organize publication categories", stats["total_categories"], "dashboard:category_list", "category"),
        ("media", "Media Library", "Upload and manage media files", stats["total_media"], "dashboard:media_list", "perm_media"),
        ("comments", "Comments", "Moderate reader comments", stats["total_comments"], "dashboard:comment_list", "chat"),
        ("books", "Books", "Manage books and resources", stats["total_books"], "dashboard:book_list", "menu_book"),
        ("counselling", "Counselling", "Review counselling requests", stats["total_counselling"], "dashboard:counselling_requests", "support_agent"),
        ("contact", "Contact Messages", "Read contact form submissions", stats["total_contact"], "dashboard:contact_list", "contact_mail"),
        ("donations", "Donations", "Track donation pledges", stats["total_donations"], "dashboard:donation_list", "volunteer_activism"),
        ("ads", "Advertisements", "Manage site advertisements", stats["total_ads"], "dashboard:ad_list", "campaign"),
        ("partners", "Partners", "Manage partner logos and links", stats["total_partners"], "dashboard:partner_list", "handshake"),
        ("menus", "Menus", "Configure navigation menus", stats["total_menus"], "dashboard:menu_list", "menu"),
        ("users", "Users", "Manage dashboard users and roles", stats["total_users"], "dashboard:user_list", "group"),
        ("settings", "Settings", "Site-wide configuration", 1 if stats["has_settings"] else 0, "dashboard:settings", "settings"),
    ]
    return [c for c in cards if user_can_access_module(user, c[0])]
