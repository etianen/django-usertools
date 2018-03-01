from django.conf.urls import url
from django.contrib import admin
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Password reset workflow.
    url("^password-reset/$", auth_views.password_reset, name="admin_password_reset", kwargs={
        "email_template_name": "admin/auth/user/password_reset_email.txt",
    }),
    url("^password-reset/complete/$", auth_views.password_reset_done, name="password_reset_done"),
    url(
        "^password-reset/token/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        auth_views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    url("^password-reset/token/complete/$", auth_views.password_reset_complete, name="password_reset_complete", kwargs={
        "extra_context": {
            "login_url": reverse_lazy("{app_name}:index".format(app_name=admin.site.name)),
        },
    }),
]
