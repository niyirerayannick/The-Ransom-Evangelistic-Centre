from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from .views import PostCreateView


class PostCreateRedirectTests(SimpleTestCase):
    def setUp(self):
        self.view = PostCreateView()
        self.request_factory = RequestFactory()

    def test_saved_post_redirects_to_post_list(self):
        request = self.request_factory.post(
            reverse("dashboard:post_create"),
            {"action": "save_draft"},
        )

        response = self.view._redirect_after_save(request, SimpleNamespace(pk=1))

        self.assertRedirects(
            response,
            reverse("dashboard:post_list"),
            fetch_redirect_response=False,
        )

    def test_preview_action_still_redirects_to_preview(self):
        request = self.request_factory.post(
            reverse("dashboard:post_create"),
            {"action": "preview"},
        )

        response = self.view._redirect_after_save(request, SimpleNamespace(pk=1))

        self.assertRedirects(
            response,
            reverse("dashboard:post_preview", kwargs={"pk": 1}),
            fetch_redirect_response=False,
        )
