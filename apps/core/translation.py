from modeltranslation.translator import translator, TranslationOptions
from .models import Advertisement, HomepageSection, Menu, MenuItem, Partner, SiteSetting, Slider


class SiteSettingTranslationOptions(TranslationOptions):
    fields = ("site_name", "tagline", "footer_text", "address_line_1", "address_line_2", "copyright_text")


class MenuTranslationOptions(TranslationOptions):
    fields = ("title",)


class MenuItemTranslationOptions(TranslationOptions):
    fields = ("title", "url")


class HomepageSectionTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle", "content", "button_text")


class AdvertisementTranslationOptions(TranslationOptions):
    fields = ("title",)


class PartnerTranslationOptions(TranslationOptions):
    fields = ("name",)


class SliderTranslationOptions(TranslationOptions):
    fields = ("subtitle",)


translator.register(SiteSetting, SiteSettingTranslationOptions)
translator.register(Menu, MenuTranslationOptions)
translator.register(MenuItem, MenuItemTranslationOptions)
translator.register(HomepageSection, HomepageSectionTranslationOptions)
translator.register(Slider, SliderTranslationOptions)
translator.register(Advertisement, AdvertisementTranslationOptions)
translator.register(Partner, PartnerTranslationOptions)
