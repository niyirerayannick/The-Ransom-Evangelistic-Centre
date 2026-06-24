from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from .forms import NewsletterForm
from .models import Subscriber


@require_POST
def subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, _("Thank you for subscribing!"))
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect(request.META.get("HTTP_REFERER", "/"))


def unsubscribe(request, email):
    subscriber = get_object_or_404(Subscriber, email=email)
    subscriber.is_active = False
    subscriber.save()
    messages.success(request, _("You have been unsubscribed."))
    return redirect("/")
