import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from apps.news.models import Post
from apps.core.models import ImportSource
from django.contrib.contenttypes.models import ContentType

ct = ContentType.objects.get_for_model(Post)
p = Post.objects.filter(status="published", title_rw__gt="").exclude(title_en__gt="").first()
if p:
    print("Post", p.pk)
    print(" title:", repr(p.title[:60]))
    print(" title_en:", repr((p.title_en or "")[:60]))
    print(" title_rw:", repr((p.title_rw or "")[:60]))
    sources = ImportSource.objects.filter(content_type=ct, object_id=p.pk)
    print(" sources:", list(sources.values_list("source_language", flat=True)))
