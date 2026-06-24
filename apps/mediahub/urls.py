from django.urls import path
from . import views

app_name = "mediahub"

urlpatterns = [
    path("galleries/", views.GalleryListView.as_view(), name="gallery_list"),
    path("galleries/<slug:slug>/", views.GalleryDetailView.as_view(), name="gallery_detail"),
    path("videos/", views.VideoListView.as_view(), name="video_list"),
]
