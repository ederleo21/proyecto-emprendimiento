from django.urls import path

from api.v1.auth.views import RefreshView, SignInView

urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='auth-sign-in'),
    path('refresh/', RefreshView.as_view(), name='auth-refresh'),
]
