from .navigation import sidebar_navigation


def dashboard_navigation(request):
    if not request.path.startswith("/dashboard"):
        return {}
    user = request.user
    if not user.is_authenticated:
        return {}
    return {
        "dashboard_sidebar": sidebar_navigation(user),
    }
