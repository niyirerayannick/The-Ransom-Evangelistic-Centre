from django.db import models
from django.utils.translation import gettext_lazy as _


class MediaFile(models.Model):
    title = models.CharField(max_length=300)
    file = models.FileField(upload_to="mediafiles/")
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    alt_text = models.CharField(max_length=300, blank=True)
    caption = models.TextField(blank=True)
    file_type = models.CharField(max_length=50, blank=True, editable=False)
    file_size = models.IntegerField(default=0, editable=False)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Media File")
        verbose_name_plural = _("Media Files")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Gallery(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=400, unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="galleries/", blank=True)
    images = models.ManyToManyField(MediaFile, blank=True, related_name="galleries")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("mediahub:gallery_detail", kwargs={"slug": self.slug})


class Video(models.Model):
    title = models.CharField(max_length=300)
    embed_url = models.URLField(help_text=_("YouTube or Vimeo embed URL"))
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="videos/", blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
