from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog, set_language
from apps.core.views import HomeView, advertisement_click
from apps.pages.views import PageDetailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", HomeView.as_view(), name="home"),
    path("advertisement/<int:pk>/click/", advertisement_click, name="advertisement_click"),
    path("news/", include("apps.news.urls")),
    path("page/<slug:slug>/", PageDetailView.as_view(), name="legacy_page_detail"),
    path("media-hub/", include("apps.mediahub.urls")),
    path("comments/", include("apps.comments.urls")),
    path("newsletter/", include("apps.newsletter.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("search/", include("apps.search.urls")),
    path("", include("apps.pages.urls")),
    prefix_default_language=True,
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
