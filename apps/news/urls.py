from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category_detail"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag_detail"),
    path("author/<str:username>/", views.AuthorPostView.as_view(), name="author_posts"),
    path("<int:year>/<int:month>/<int:day>/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail_slug"),
]
