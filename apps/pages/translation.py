from modeltranslation.translator import translator, TranslationOptions
from .models import Book, BookCategory, Counsellor, DonationMethod, DonationProgram, LeadershipMember, Page


class PageTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "slug",
        "content",
        "excerpt",
        "meta_title",
        "meta_description",
    )


translator.register(Page, PageTranslationOptions)


class LeadershipMemberTranslationOptions(TranslationOptions):
    fields = ("name", "role", "bio")


class BookCategoryTranslationOptions(TranslationOptions):
    fields = ("name", "description")


class BookTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class DonationMethodTranslationOptions(TranslationOptions):
    fields = ("name", "instructions")


class DonationProgramTranslationOptions(TranslationOptions):
    fields = ("title", "description")


class CounsellorTranslationOptions(TranslationOptions):
    fields = ("name", "role", "bio")


translator.register(DonationMethod, DonationMethodTranslationOptions)
translator.register(DonationProgram, DonationProgramTranslationOptions)
translator.register(Counsellor, CounsellorTranslationOptions)
translator.register(LeadershipMember, LeadershipMemberTranslationOptions)
translator.register(BookCategory, BookCategoryTranslationOptions)
translator.register(Book, BookTranslationOptions)
