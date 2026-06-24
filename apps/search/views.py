from django.views.generic import TemplateView
from django.db.models import Q
from django.utils.translation import get_language
from apps.news.models import Post
from apps.news.homepage import posts_for_language, normalize_language_code
from apps.pages.models import Page


class SearchView(TemplateView):
    template_name = "search/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        language = normalize_language_code(get_language())
        context["query"] = query

        if query:
            post_filter = (
                Q(**{f"title_{language}__icontains": query})
                | Q(**{f"excerpt_{language}__icontains": query})
                | Q(**{f"content_{language}__icontains": query})
            )
            if language == "en":
                post_filter |= (
                    Q(title__icontains=query)
                    | Q(excerpt__icontains=query)
                    | Q(content__icontains=query)
                )

            page_filter = (
                Q(**{f"title_{language}__icontains": query})
                | Q(**{f"content_{language}__icontains": query})
                | Q(**{f"excerpt_{language}__icontains": query})
            )
            if language == "en":
                page_filter |= Q(title__icontains=query) | Q(content__icontains=query)

            posts = posts_for_language(language).filter(post_filter).distinct()
            pages = Page.objects.filter(is_published=True).filter(page_filter).distinct()
            context["posts"] = posts
            context["pages"] = pages
            context["total_results"] = posts.count() + pages.count()
        else:
            context["posts"] = Post.objects.none()
            context["pages"] = Page.objects.none()
            context["total_results"] = 0

        return context
