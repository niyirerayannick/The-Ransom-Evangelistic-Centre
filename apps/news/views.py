from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import get_language

from apps.core.language_flags import LANGUAGE_META
from .models import Post, Category, Tag
from .homepage import posts_for_language, normalize_language_code
from .i18n_urls import category_url_for_language
from apps.comments.forms import CommentForm
from apps.core.models import Advertisement


class PostListView(ListView):
    model = Post
    template_name = "news/post_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        return posts_for_language(get_language())


class PostDetailView(DetailView):
    model = Post
    template_name = "news/post_detail.html"
    context_object_name = "post"

    def get_object(self):
        slug = self.kwargs.get("slug")
        language = normalize_language_code(get_language())
        queryset = Post.objects.filter(status="published").select_related(
            "category", "author"
        ).prefetch_related("tags")
        if all(self.kwargs.get(part) is not None for part in ("year", "month", "day")):
            queryset = queryset.filter(
                published_at__year=self.kwargs["year"],
                published_at__month=self.kwargs["month"],
                published_at__day=self.kwargs["day"],
            )

        post = queryset.filter(**{f"slug_{language}": slug}).first()
        if not post:
            for other_lang in Post.LANGUAGE_CODES:
                if other_lang == language:
                    continue
                post = queryset.filter(**{f"slug_{other_lang}": slug}).first()
                if post:
                    break
        if not post and language == "en":
            post = queryset.filter(slug=slug).first()

        if not post:
            raise Http404

        self._resolved_post = post
        self._requested_language = language
        return post

    def get_template_names(self):
        post = getattr(self, "_resolved_post", None) or self.object
        language = getattr(self, "_requested_language", normalize_language_code(get_language()))
        if post and not post.is_available_in_language(language):
            return ["news/post_unavailable.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        language = normalize_language_code(get_language())

        if not post.is_available_in_language(language):
            context["requested_language"] = language
            context["available_language_links"] = self._language_links(post)
            return context

        post.increment_views()
        post.views_count += 1

        lang_posts = posts_for_language(language)
        context["display_title"] = post.title_for_language(language, fallback=False)
        context["display_excerpt"] = post.excerpt_for_language(language, fallback=False)
        context["display_content"] = post.content_for_language(language, fallback=False)
        context["display_seo_title"] = post.field_for_language("seo_title", language, fallback=False)
        context["display_meta_description"] = post.field_for_language("meta_description", language, fallback=False)
        context["available_language_links"] = self._language_links(post)
        context["related_posts"] = lang_posts.filter(category=post.category).exclude(pk=post.pk)[:4]
        context["latest_posts"] = lang_posts.exclude(pk=post.pk)[:5]
        context["previous_post"] = (
            lang_posts.filter(published_at__lt=post.published_at).first()
            if post.published_at else None
        )
        context["next_post"] = (
            lang_posts.filter(published_at__gt=post.published_at).order_by("published_at").first()
            if post.published_at else None
        )

        now = timezone.now()
        active_ads = Advertisement.objects.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )
        context["article_top_ad"] = active_ads.filter(position="article_top").first()
        context["article_bottom_ad"] = active_ads.filter(position="article_bottom").first()
        context["sidebar_ad"] = active_ads.filter(position="sidebar").first()
        context["comment_form"] = CommentForm()
        context["comments"] = post.comments.filter(status="approved", parent__isnull=True)
        return context

    def _language_links(self, post):
        from apps.news.i18n_urls import post_url_for_language

        labels = {code: meta["label"] for code, meta in LANGUAGE_META.items()}
        flag_urls = {code: meta["flag_url"] for code, meta in LANGUAGE_META.items()}
        links = []
        for lang in Post.LANGUAGE_CODES:
            url = post_url_for_language(post, lang)
            if not url:
                continue
            links.append({
                "code": lang,
                "label": labels[lang],
                "flag_url": flag_urls[lang],
                "url": url,
            })
        return links


class CategoryView(ListView):
    model = Post
    template_name = "news/category_detail.html"
    context_object_name = "posts"
    paginate_by = 12

    def _resolve_category(self):
        slug = self.kwargs["slug"]
        language = normalize_language_code(get_language())
        queryset = Category.objects.filter(is_active=True)
        self.category = queryset.filter(**{f"slug_{language}": slug}).first()
        if not self.category:
            self.category = queryset.filter(
                Q(slug_en=slug) | Q(slug_fr=slug) | Q(slug_rw=slug) | Q(slug=slug)
            ).first()
        if not self.category:
            raise Http404
        self.current_language = language

    def get_queryset(self):
        if not hasattr(self, "category"):
            self._resolve_category()
        return posts_for_language(self.current_language).filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.current_language
        category = self.category

        display_name = category.field_for_language("name", language)
        display_description = category.field_for_language("description", language)
        site_name = ""
        try:
            from apps.core.models import SiteSetting
            site_name = SiteSetting.objects.values_list("site_name", flat=True).first() or ""
        except Exception:
            pass

        if display_description:
            meta_description = display_description
        else:
            meta_description = (
                f"Explore articles about {display_name} from {site_name}."
                if site_name
                else f"Explore articles about {display_name}."
            )

        seo_title = f"{display_name} Articles"
        if site_name:
            seo_title = f"{seo_title} | {site_name}"

        context.update({
            "category": category,
            "current_language": language,
            "display_category_name": display_name,
            "display_category_description": display_description,
            "display_seo_title": seo_title,
            "display_meta_description": meta_description,
            "canonical_url": self.request.build_absolute_uri(
                category_url_for_language(category, language)
            ),
        })
        return context


class TagView(ListView):
    model = Post
    template_name = "news/tag_detail.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        slug = self.kwargs["slug"]
        language = normalize_language_code(get_language())
        self.tag = Tag.objects.filter(**{f"slug_{language}": slug}).first()
        if not self.tag:
            self.tag = Tag.objects.filter(
                Q(slug_en=slug) | Q(slug_fr=slug) | Q(slug_rw=slug) | Q(slug=slug)
            ).first()
        if not self.tag:
            raise Http404
        return posts_for_language(language).filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class AuthorPostView(ListView):
    model = Post
    template_name = "news/author_posts.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        return posts_for_language(get_language()).filter(
            author__username=self.kwargs["username"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth import get_user_model
        context["author"] = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        return context
