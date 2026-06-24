from django.utils.translation import get_language
from .homepage import posts_for_language, normalize_language_code


def breaking_news(request):
    language = normalize_language_code(get_language())
    breaking = posts_for_language(language).filter(is_breaking=True)[:5]
    return {"breaking_news": breaking}
