from django.db.models import F, Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import get_language
from django.views.generic import TemplateView
from .models import Advertisement, HomepageSection, Partner
from .homepage_content import WHO_WE_ARE_KEY, sync_who_we_are_section
from apps.news.homepage import posts_for_language, posts_for_home_section, normalize_language_code, category_for_home_section


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = normalize_language_code(get_language())
        base_posts = posts_for_language(language)

        featured_post = base_posts.filter(is_featured=True).first() or base_posts.first()
        now = timezone.now()
        active_ads = Advertisement.objects.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )

        context.update({
            "current_language": language,
            "featured_post": featured_post,
            "church_posts": posts_for_home_section("church", 3, language),
            "leadership_posts": posts_for_home_section("leadership", 3, language),
            "family_posts": posts_for_home_section("family", 5, language),
            "criticism_posts": posts_for_home_section("constructive-criticism", 5, language),
            "healing_posts": posts_for_home_section("healing", 5, language),
            "church_category": category_for_home_section("church", language),
            "leadership_category": category_for_home_section("leadership", language),
            "family_category": category_for_home_section("family", language),
            "criticism_category": category_for_home_section("constructive-criticism", language),
            "healing_category": category_for_home_section("healing", language),
            "latest_posts": list(base_posts[:4]),
            "who_we_are": (
                HomepageSection.objects.filter(is_active=True, key=WHO_WE_ARE_KEY).first()
                or sync_who_we_are_section()
            ),
            "home_after_featured_ad": active_ads.filter(
                position="home_after_featured"
            ).first(),
            "partners": Partner.objects.filter(is_active=True),
        })
        return context


def advertisement_click(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk, is_active=True)
    if not advertisement.is_current or not advertisement.link:
        raise Http404
    Advertisement.objects.filter(pk=pk).update(clicks=F("clicks") + 1)
    return redirect(advertisement.link)


def health_check(request):
    return HttpResponse("ok", content_type="text/plain")
