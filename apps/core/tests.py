from django.test import Client, TestCase

from .models import Redirect


class LegacyRedirectMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="yvesgashugi.org")

    def test_site_root_redirects_to_english_homepage_not_an_article(self):
        Redirect.objects.create(
            old_url="https://yvesgashugi.org/2023/07/11/old-article/",
            new_url="/en/news/2023/7/11/old-article/",
            source_language="en",
        )

        response = self.client.get("/")

        self.assertRedirects(
            response,
            "/en/",
            status_code=302,
            fetch_redirect_response=False,
        )
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_imported_redirect_matches_the_exact_path(self):
        Redirect.objects.create(
            old_url="https://yvesgashugi.org/news/old-article/",
            new_url="/en/news/old-article/",
            source_language="en",
        )

        response = self.client.get("/news/old-article/")

        self.assertRedirects(
            response,
            "/en/news/old-article/",
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_imported_redirect_does_not_match_only_a_path_suffix(self):
        Redirect.objects.create(
            old_url="https://yvesgashugi.org/news/old-article/",
            new_url="/en/news/old-article/",
            source_language="en",
        )

        response = self.client.get("/old-article/")

        self.assertNotEqual(response.status_code, 301)
