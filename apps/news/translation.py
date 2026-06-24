from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Post, Tag


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name", "slug", "description")


class PostTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "excerpt", "content", "seo_title", "meta_description")


class TagTranslationOptions(TranslationOptions):
    fields = ("name", "slug")


translator.register(Category, CategoryTranslationOptions)
translator.register(Post, PostTranslationOptions)
translator.register(Tag, TagTranslationOptions)
