from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("books/<slug:slug>/read/", views.BookReaderView.as_view(), name="book_reader"),
    path("books/<slug:slug>/pdf/", views.BookPdfView.as_view(), name="book_pdf"),
    path(
        "books/<slug:slug>/page/<int:page_num>/",
        views.BookPageImageView.as_view(),
        name="book_page_image",
    ),
    path("<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
]
