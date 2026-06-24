from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.accounts.models import User
from apps.news.models import Post, MediaLibrary
from apps.pages.models import ContactMessage, CounsellingRequest
from .forms import PostAuthorForm, MediaUploadForm, PostReviewForm
from .permissions import DashboardAccessMixin, PostAccessMixin
from .stats import dashboard_stats, module_cards


class DashboardHomeView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/index.html"
    module_key = "home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        stats = dashboard_stats(user)
        context["stats"] = stats
        context["module_cards"] = module_cards(user)

        posts = Post.objects.select_related("category", "author")
        if not (user.is_superuser or user.role in ("super_admin", "admin", "editor", "viewer")):
            posts = posts.filter(author=user)

        context["recent_posts"] = posts.order_by("-updated_at")[:8]
        context["posts_by_status"] = list(
            posts.values("status").annotate(count=Count("id")).order_by("status")
        )
        context["posts_by_language"] = [
            {"lang": "EN", "count": stats["posts_en"]},
            {"lang": "FR", "count": stats["posts_fr"]},
            {"lang": "RW", "count": stats["posts_rw"]},
        ]

        if user.can_review_posts():
            context["pending_posts"] = Post.objects.filter(
                status=Post.STATUS_PENDING_REVIEW
            ).select_related("author", "category").order_by("-updated_at")[:10]

        if user_can_access_engagement(user):
            context["recent_contacts"] = ContactMessage.objects.order_by("-created_at")[:5]
            context["recent_counselling"] = CounsellingRequest.objects.order_by("-created_at")[:5]

        return context


def user_can_access_engagement(user):
    from .roles import user_can_access_module
    return user_can_access_module(user, "contact") or user_can_access_module(user, "counselling")


class PostListView(PostAccessMixin, ListView):
    template_name = "dashboard/posts/list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        from apps.news.homepage import post_available_in_language_q

        queryset = self.get_post_queryset()
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        author = self.request.GET.get("author")
        if author and self.request.user.is_admin_role:
            queryset = queryset.filter(author_id=author)
        lang_filter = self.request.GET.get("lang")
        if lang_filter == "missing_fr":
            queryset = queryset.exclude(post_available_in_language_q("fr"))
        elif lang_filter == "missing_rw":
            queryset = queryset.exclude(post_available_in_language_q("rw"))
        elif lang_filter == "missing_en":
            queryset = queryset.exclude(post_available_in_language_q("en"))
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title_en__icontains=search)
                | Q(title_fr__icontains=search)
                | Q(title_rw__icontains=search)
                | Q(content_en__icontains=search)
            )
        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        from apps.news.models import Category

        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True).order_by("name")
        if self.request.user.is_admin_role:
            context["authors"] = User.objects.filter(
                role__in=("author", "editor", "admin")
            ).order_by("username")
        return context

    def post(self, request):
        if not request.user.can_review_posts() and request.POST.get("bulk_action") != "delete_draft":
            raise PermissionDenied
        action = request.POST.get("bulk_action")
        ids = request.POST.getlist("selected_posts")
        if not ids:
            messages.warning(request, _("No posts selected."))
            return redirect("dashboard:post_list")
        queryset = self.get_post_queryset().filter(pk__in=ids)
        count = 0
        if action == "publish" and request.user.can_publish_posts():
            count = queryset.update(status=Post.STATUS_PUBLISHED, published_at=timezone.now())
            messages.success(request, _("%(count)d post(s) published.") % {"count": count})
        elif action == "submit_review":
            count = queryset.filter(status__in=(Post.STATUS_DRAFT, Post.STATUS_REJECTED)).update(
                status=Post.STATUS_PENDING_REVIEW
            )
            messages.success(request, _("%(count)d post(s) submitted for review.") % {"count": count})
        elif action == "delete_draft":
            deleted = 0
            for post in queryset:
                if request.user.can_delete_post(post) and post.status == Post.STATUS_DRAFT:
                    post.delete()
                    deleted += 1
            messages.success(request, _("%(count)d draft(s) deleted.") % {"count": deleted})
        else:
            messages.error(request, _("Invalid bulk action."))
        return redirect(request.get_full_path() or reverse("dashboard:post_list"))


class PostCreateView(DashboardAccessMixin, View):
    template_name = "dashboard/post_form.html"
    module_key = "posts"

    def dispatch(self, request, *args, **kwargs):
        from .roles import user_can_write_module
        if not user_can_write_module(request.user, "posts"):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = PostAuthorForm(user=request.user)
        return render(request, self.template_name, self._form_context(form))

    def post(self, request):
        form = PostAuthorForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = self._save_post(form, request)
            messages.success(request, _("Post saved successfully."))
            return self._redirect_after_save(request, post)
        return render(request, self.template_name, self._form_context(form))

    def _form_context(self, form, post=None):
        return {
            "form": form,
            "post": post,
            "is_create": post is None,
            "review_form": PostReviewForm(),
            "all_tags": form.fields["tags"].queryset,
        }

    def _save_post(self, form, request):
        post = form.save(commit=False)
        post.author = request.user
        action = request.POST.get("action", "save_draft")
        if action == "submit_review":
            post.status = Post.STATUS_PENDING_REVIEW
        elif action == "save_draft":
            post.status = Post.STATUS_DRAFT
        elif action == "publish" and request.user.can_publish_posts():
            post.status = Post.STATUS_PUBLISHED
            if not post.published_at:
                post.published_at = timezone.now()
        elif not request.user.can_publish_posts():
            post.status = Post.STATUS_DRAFT
        post.title = post.title_en or post.title
        post.slug = post.slug_en or post.slug
        post.content = post.content_en or post.content
        post.save()
        form.save_m2m()
        return post

    def _redirect_after_save(self, request, post):
        action = request.POST.get("action")
        if action == "preview":
            return redirect("dashboard:post_preview", pk=post.pk)
        return redirect("dashboard:post_edit", pk=post.pk)


class PostEditView(PostAccessMixin, View):
    template_name = "dashboard/post_form.html"

    def get(self, request, pk):
        post = self.get_post()
        if not request.user.can_edit_post(post):
            raise PermissionDenied
        form = PostAuthorForm(instance=post, user=request.user)
        return render(request, self.template_name, self._form_context(form, post))

    def post(self, request, pk):
        post = self.get_post()
        if not request.user.can_edit_post(post):
            raise PermissionDenied
        form = PostAuthorForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            post = self._save_post(form, request, post)
            messages.success(request, _("Post updated successfully."))
            return self._redirect_after_save(request, post)
        return render(request, self.template_name, self._form_context(form, post))

    def _form_context(self, form, post):
        return {
            "form": form,
            "post": post,
            "is_create": False,
            "review_form": PostReviewForm(),
            "all_tags": form.fields["tags"].queryset,
        }

    def _save_post(self, form, request, post):
        post = form.save(commit=False)
        action = request.POST.get("action", "save_draft")
        if action == "submit_review":
            post.status = Post.STATUS_PENDING_REVIEW
        elif action == "save_draft":
            if post.status not in (Post.STATUS_PUBLISHED, Post.STATUS_ARCHIVED):
                post.status = Post.STATUS_DRAFT
        elif action == "publish" and request.user.can_publish_posts():
            post.status = Post.STATUS_PUBLISHED
            if not post.published_at:
                post.published_at = timezone.now()
        elif action == "archive" and request.user.can_publish_posts():
            post.status = Post.STATUS_ARCHIVED
        post.title = post.title_en or post.title
        post.slug = post.slug_en or post.slug
        post.content = post.content_en or post.content
        post.save()
        form.save_m2m()
        return post

    def _redirect_after_save(self, request, post):
        action = request.POST.get("action")
        if action == "preview":
            return redirect("dashboard:post_preview", pk=post.pk)
        return redirect("dashboard:post_edit", pk=post.pk)


class PostPreviewView(PostAccessMixin, TemplateView):
    template_name = "dashboard/post_preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_post()
        lang = self.request.GET.get("lang", "en")
        if lang not in Post.LANGUAGE_CODES:
            lang = "en"

        def localized(field):
            value, using_fallback = post.get_localized_field(field, lang)
            return value, using_fallback

        title, title_fallback = localized("title")
        excerpt, excerpt_fallback = localized("excerpt")
        content, content_fallback = localized("content")
        seo_title, _ = localized("seo_title")
        meta_description, _ = localized("meta_description")

        context.update({
            "post": post,
            "preview_lang": lang,
            "preview_title": title,
            "preview_excerpt": excerpt,
            "preview_content": content,
            "preview_seo_title": seo_title,
            "preview_meta_description": meta_description,
            "using_fallback": title_fallback or content_fallback or excerpt_fallback,
            "language_codes": Post.LANGUAGE_CODES,
        })
        return context


class PostSubmitReviewView(PostAccessMixin, View):
    def post(self, request, pk):
        post = self.get_post()
        if post.author_id != request.user.pk and not request.user.can_review_posts():
            raise PermissionDenied
        if post.status not in (Post.STATUS_DRAFT, Post.STATUS_REJECTED):
            messages.error(request, _("Only draft or rejected posts can be submitted for review."))
        else:
            post.status = Post.STATUS_PENDING_REVIEW
            post.rejection_reason = ""
            post.save(update_fields=["status", "rejection_reason", "updated_at"])
            messages.success(request, _("Post submitted for review."))
        return redirect("dashboard:post_list")


class PostDeleteView(PostAccessMixin, View):
    def post(self, request, pk):
        post = self.get_post()
        if not request.user.can_delete_post(post):
            raise PermissionDenied
        post.delete()
        messages.success(request, _("Draft post deleted."))
        return redirect("dashboard:post_list")


class PostReviewActionView(PostAccessMixin, View):
    def post(self, request, pk):
        if not request.user.can_review_posts():
            raise PermissionDenied
        post = get_object_or_404(Post, pk=pk)
        action = request.POST.get("action")
        reason = request.POST.get("rejection_reason", "").strip()
        now = timezone.now()

        if action == PostReviewForm.ACTION_PUBLISH:
            post.status = Post.STATUS_PUBLISHED
            post.reviewed_by = request.user
            post.reviewed_at = now
            post.rejection_reason = ""
            if not post.published_at:
                post.published_at = now
            messages.success(request, _("Post published."))
        elif action == PostReviewForm.ACTION_REJECT:
            post.status = Post.STATUS_REJECTED
            post.reviewed_by = request.user
            post.reviewed_at = now
            post.rejection_reason = reason or _("Rejected by editor.")
            messages.warning(request, _("Post rejected."))
        elif action == PostReviewForm.ACTION_SEND_BACK:
            post.status = Post.STATUS_DRAFT
            post.reviewed_by = request.user
            post.reviewed_at = now
            post.rejection_reason = reason
            messages.info(request, _("Post sent back to author for correction."))
        else:
            messages.error(request, _("Invalid review action."))
            return redirect("dashboard:post_edit", pk=pk)

        post.save()
        return redirect("dashboard:post_edit", pk=pk)


class MediaLibraryView(DashboardAccessMixin, View):
    template_name = "dashboard/media_list.html"
    module_key = "media"

    def get(self, request):
        form = MediaUploadForm()
        media_items = self._media_queryset(request.user)
        return render(request, self.template_name, {"form": form, "media_items": media_items})

    def post(self, request):
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, _("File uploaded successfully."))
            return redirect("dashboard:media_list")
        media_items = self._media_queryset(request.user)
        return render(request, self.template_name, {"form": form, "media_items": media_items})

    def _media_queryset(self, user):
        queryset = MediaLibrary.objects.select_related("uploaded_by")
        if not (user.is_superuser or user.role in ("super_admin", "admin", "editor", "viewer")):
            queryset = queryset.filter(uploaded_by=user)
        return queryset.order_by("-created_at")
