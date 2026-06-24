from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Gallery, Video


class GalleryListView(ListView):
    model = Gallery
    template_name = "mediahub/gallery_list.html"
    context_object_name = "galleries"
    paginate_by = 12

    def get_queryset(self):
        return Gallery.objects.filter(is_published=True)


class GalleryDetailView(DetailView):
    model = Gallery
    template_name = "mediahub/gallery_detail.html"
    context_object_name = "gallery"

    def get_object(self):
        return get_object_or_404(Gallery, slug=self.kwargs["slug"], is_published=True)


class VideoListView(ListView):
    model = Video
    template_name = "mediahub/video_list.html"
    context_object_name = "videos"
    paginate_by = 12

    def get_queryset(self):
        return Video.objects.filter(is_published=True)
