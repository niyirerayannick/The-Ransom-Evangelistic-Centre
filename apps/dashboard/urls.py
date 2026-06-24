from django.urls import path

from . import views
from .views_auth import (
    AuditLogView,
    DashboardLoginView,
    DashboardLogoutView,
    ProfileView,
    RolesPermissionsView,
)
from .views_module_crud import ModuleCreateView, ModuleDeleteView, ModuleEditView
from .views_who_we_are import WhoWeAreEditView
from .views_team import TeamCreateView, TeamDeleteView, TeamEditView, TeamListView, TeamToggleActiveView
from .views_counsellors import (
    CounsellingRequestEditView,
    CounsellingRequestListView,
    CounsellorDeleteView,
    CounsellorEditView,
    CounsellorListView,
    CounsellorToggleActiveView,
)
from .views_donations import (
    DonationMethodDeleteView,
    DonationMethodEditView,
    DonationMethodListView,
    DonationPledgeEditView,
    DonationPledgeExportView,
    DonationPledgeListView,
    DonationProgramDeleteView,
    DonationProgramEditView,
    DonationProgramListView,
)
from .views_modules import (
    AdListView,
    BookListView,
    CategoryListView,
    CommentListView,
    ContactListView,
    CounsellingListView,
    DonationListView,
    HomepageSectionListView,
    MenuListView,
    PageListView,
    PartnerListView,
    SettingsView,
    SubscriberListView,
    TagListView,
)
from .views_users import (
    UserCreateView,
    UserDeleteView,
    UserEditView,
    UserListView,
    UserResetPasswordView,
    UserToggleActiveView,
)

app_name = "dashboard"


def _crud(prefix, registry_key, name):
    """Generate create/edit/delete URL patterns for a module."""
    return [
        path(f"{prefix}create/", ModuleCreateView.as_view(registry_key=registry_key), name=f"{name}_create"),
        path(f"{prefix}<int:pk>/edit/", ModuleEditView.as_view(registry_key=registry_key), name=f"{name}_edit"),
        path(f"{prefix}<int:pk>/delete/", ModuleDeleteView.as_view(registry_key=registry_key), name=f"{name}_delete"),
    ]


def _edit_only(prefix, registry_key, name):
    """Edit/delete only (no public create — e.g. form submissions)."""
    return [
        path(f"{prefix}<int:pk>/edit/", ModuleEditView.as_view(registry_key=registry_key), name=f"{name}_edit"),
        path(f"{prefix}<int:pk>/delete/", ModuleDeleteView.as_view(registry_key=registry_key), name=f"{name}_delete"),
    ]


urlpatterns = [
    path("login/", DashboardLoginView.as_view(), name="login"),
    path("logout/", DashboardLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", UserEditView.as_view(), name="user_edit"),
    path("users/<int:pk>/toggle-active/", UserToggleActiveView.as_view(), name="user_toggle_active"),
    path("users/<int:pk>/reset-password/", UserResetPasswordView.as_view(), name="user_reset_password"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("roles/", RolesPermissionsView.as_view(), name="roles"),
    path("audit-logs/", AuditLogView.as_view(), name="audit_logs"),
    path("posts/", views.PostListView.as_view(), name="post_list"),
    path("posts/create/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", views.PostEditView.as_view(), name="post_edit"),
    path("posts/<int:pk>/preview/", views.PostPreviewView.as_view(), name="post_preview"),
    path("posts/<int:pk>/submit/", views.PostSubmitReviewView.as_view(), name="post_submit"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("posts/<int:pk>/review/", views.PostReviewActionView.as_view(), name="post_review"),
    path("pages/", PageListView.as_view(), name="page_list"),
    path("team/", TeamListView.as_view(), name="team_list"),
    path("team/create/", TeamCreateView.as_view(), name="team_create"),
    path("team/<int:pk>/edit/", TeamEditView.as_view(), name="team_edit"),
    path("team/<int:pk>/toggle-active/", TeamToggleActiveView.as_view(), name="team_toggle_active"),
    path("team/<int:pk>/delete/", TeamDeleteView.as_view(), name="team_delete"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("tags/", TagListView.as_view(), name="tag_list"),
    path("media/", views.MediaLibraryView.as_view(), name="media_list"),
    path("comments/", CommentListView.as_view(), name="comment_list"),
    path("books/", BookListView.as_view(), name="book_list"),
    path("counselling/", CounsellingRequestListView.as_view(), name="counselling_list"),
    path("counselling-requests/", CounsellingRequestListView.as_view(), name="counselling_requests"),
    path("counselling-requests/<int:pk>/edit/", CounsellingRequestEditView.as_view(), name="counselling_request_edit"),
    path("counsellors/", CounsellorListView.as_view(), name="counsellor_list"),
    path("counsellors/create/", CounsellorEditView.as_view(), name="counsellor_create"),
    path("counsellors/<int:pk>/edit/", CounsellorEditView.as_view(), name="counsellor_edit"),
    path("counsellors/<int:pk>/toggle-active/", CounsellorToggleActiveView.as_view(), name="counsellor_toggle_active"),
    path("counsellors/<int:pk>/delete/", CounsellorDeleteView.as_view(), name="counsellor_delete"),
    path("contact-messages/", ContactListView.as_view(), name="contact_list"),
    path("donations/", DonationPledgeListView.as_view(), name="donation_list"),
    path("donations/pledges/", DonationPledgeListView.as_view(), name="donation_pledges"),
    path("donations/pledges/export/", DonationPledgeExportView.as_view(), name="donation_pledges_export"),
    path("donations/pledges/<int:pk>/edit/", DonationPledgeEditView.as_view(), name="donation_pledge_edit"),
    path("donations/methods/", DonationMethodListView.as_view(), name="donation_methods"),
    path("donations/methods/create/", DonationMethodEditView.as_view(), name="donation_method_create"),
    path("donations/methods/<int:pk>/edit/", DonationMethodEditView.as_view(), name="donation_method_edit"),
    path("donations/methods/<int:pk>/delete/", DonationMethodDeleteView.as_view(), name="donation_method_delete"),
    path("donations/programs/", DonationProgramListView.as_view(), name="donation_programs"),
    path("donations/programs/create/", DonationProgramEditView.as_view(), name="donation_program_create"),
    path("donations/programs/<int:pk>/edit/", DonationProgramEditView.as_view(), name="donation_program_edit"),
    path("donations/programs/<int:pk>/delete/", DonationProgramDeleteView.as_view(), name="donation_program_delete"),
    path("ads/", AdListView.as_view(), name="ad_list"),
    path("partners/", PartnerListView.as_view(), name="partner_list"),
    path("menus/", MenuListView.as_view(), name="menu_list"),
    path("homepage-sections/", HomepageSectionListView.as_view(), name="homepage_list"),
    path("homepage/who-we-are/", WhoWeAreEditView.as_view(), name="who_we_are_edit"),
    path("subscribers/", SubscriberListView.as_view(), name="subscriber_list"),
    path("settings/", SettingsView.as_view(), name="settings"),
]

urlpatterns += _crud("pages/", "pages", "page")
urlpatterns += _crud("categories/", "categories", "category")
urlpatterns += _crud("tags/", "tags", "tag")
urlpatterns += _edit_only("comments/", "comments", "comment")
urlpatterns += _crud("books/", "books", "book")
urlpatterns += _edit_only("counselling/", "counselling", "counselling")
urlpatterns += _edit_only("contact-messages/", "contact", "contact")
urlpatterns += _crud("ads/", "ads", "ad")
urlpatterns += _crud("partners/", "partners", "partner")
urlpatterns += _crud("menus/", "menus", "menu")
urlpatterns += _crud("homepage-sections/", "homepage", "homepage")
urlpatterns += _crud("subscribers/", "subscribers", "subscriber")
