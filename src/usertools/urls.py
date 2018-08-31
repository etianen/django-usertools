from django.conf.urls import url
from django.contrib import admin
try:
    from django.urls import reverse_lazy
except ImportError:  # Django < 1.10 pragma: no cover
    from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Password reset workflow.
    url(
        "^password-reset/$",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
        kwargs={
            "email_template_name": "admin/auth/user/password_reset_email.txt",
        }
    ),
    url(
        "^password-reset/complete/$",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done"
    ),
    url(
        "^password-reset/token/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    url(
        "^password-reset/token/complete/$",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
        kwargs={
            "extra_context": {
                "login_url": reverse_lazy("{app_name}:index".format(app_name=admin.site.name)),
            },
        }
    ),
]
