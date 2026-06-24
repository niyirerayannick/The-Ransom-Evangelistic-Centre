"""Role and module permission definitions for the custom dashboard."""

from django.core.exceptions import PermissionDenied

MODULES = {
    "home": {"label": "Dashboard", "group": "main"},
    "posts": {"label": "Posts", "group": "content"},
    "pages": {"label": "Pages", "group": "content"},
    "team": {"label": "Team / Leadership", "group": "content"},
    "categories": {"label": "Categories", "group": "content"},
    "tags": {"label": "Tags", "group": "content"},
    "media": {"label": "Media Library", "group": "content"},
    "comments": {"label": "Comments", "group": "content"},
    "books": {"label": "Books", "group": "publishing"},
    "newsletter": {"label": "Newsletter", "group": "publishing"},
    "counselling": {"label": "Counselling Requests", "group": "engagement"},
    "counsellors": {"label": "Counsellors", "group": "engagement"},
    "contact": {"label": "Contact Messages", "group": "engagement"},
    "donations": {"label": "Donation Pledges", "group": "engagement"},
    "subscribers": {"label": "Subscribers", "group": "engagement"},
    "menus": {"label": "Menus", "group": "website"},
    "ads": {"label": "Advertisements", "group": "website"},
    "partners": {"label": "Partners", "group": "website"},
    "homepage": {"label": "Homepage Sections", "group": "website"},
    "settings": {"label": "Site Settings", "group": "website"},
    "users": {"label": "Users", "group": "administration"},
}

ROLE_MODULES = {
    "super_admin": set(MODULES.keys()),
    "admin": set(MODULES.keys()) - {"users"} | {"users"},
    "editor": {
        "home", "posts", "pages", "team", "categories", "tags", "media", "comments",
        "books", "newsletter", "counselling", "counsellors", "contact", "donations", "subscribers",
    },
    "author": {"home", "posts", "media"},
    "viewer": {
        "home", "posts", "pages", "categories", "media", "comments", "books",
        "counselling", "counsellors", "contact", "donations",
    },
}

WRITE_MODULES = {
    "super_admin": set(MODULES.keys()),
    "admin": set(MODULES.keys()),
    "editor": {
        "posts", "pages", "team", "categories", "tags", "media", "comments", "books",
        "counselling", "counsellors", "contact", "donations",
    },
    "author": {"posts", "media"},
    "viewer": set(),
}


def effective_role(user):
    if user.is_superuser:
        return "super_admin"
    return user.role or "author"


def user_can_access_module(user, module_key):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.is_active:
        return False
    role = effective_role(user)
    if role == "admin" and module_key in MODULES:
        return True
    return module_key in ROLE_MODULES.get(role, set())


def user_can_write_module(user, module_key):
    if not user_can_access_module(user, module_key):
        return False
    if user.is_superuser:
        return True
    role = effective_role(user)
    if role == "admin":
        return module_key != "users" or user.is_superuser
    return module_key in WRITE_MODULES.get(role, set())


def user_can_manage_users(user):
    if not user.is_authenticated or not user.is_active:
        return False
    role = effective_role(user)
    return user.is_superuser or role in ("super_admin", "admin")


def user_can_manage_target_user(actor, target):
    if not user_can_manage_users(actor):
        return False
    if actor.is_superuser:
        return True
    target_role = effective_role(target)
    if target_role == "super_admin" or target.is_superuser:
        return False
    return effective_role(actor) in ("super_admin", "admin")


def require_module(module_key):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not user_can_access_module(request.user, module_key):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator
