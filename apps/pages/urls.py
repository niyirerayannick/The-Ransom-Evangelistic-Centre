from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("books/<slug:slug>/read/", views.BookReaderView.as_view(), name="book_reader"),
    path("<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
]
