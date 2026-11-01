from types import SimpleNamespace

from django.test import Client, RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.core.models import Partner

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


class PartnerLogoUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="partner-admin",
            password="test-password",
            role=User.ROLE_ADMIN,
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_partner_create_form_includes_logo_upload(self):
        response = self.client.get(reverse("dashboard:partner_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="file" name="logo"')

    def test_partner_edit_form_shows_current_logo_and_upload_field(self):
        partner = Partner.objects.create(
            name="Example Partner",
            logo="partners/example.svg",
        )

        response = self.client.get(
            reverse("dashboard:partner_edit", kwargs={"pk": partner.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/media/partners/example.svg")
        self.assertContains(response, 'type="file" name="logo"')
