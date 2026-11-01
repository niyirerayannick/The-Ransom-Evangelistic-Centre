from django.test import TestCase
from apps.news.models import Post


class PostSlugTests(TestCase):
    def test_saving_posts_without_slugs_generates_unique_legacy_slugs(self):
        first = Post.objects.create(
            title="First post",
            slug="",
            content="First post content",
            title_en="First post",
            content_en="First post content",
        )
        second = Post.objects.create(
            title="Second post",
            slug="",
            content="Second post content",
            title_en="Second post",
            content_en="Second post content",
        )

        self.assertEqual(first.slug, "first-post")
        self.assertEqual(second.slug, "second-post")
