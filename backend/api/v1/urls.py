from django.urls import include, path

from api.v1.branding import BrandingAdminView, BrandingLogoView, BrandingView
from api.v1.views import HealthCheckView, WhoAmIView

app_name = 'v1'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('whoami/', WhoAmIView.as_view(), name='whoami'),
    # Pública: la pantalla de acceso necesita los colores antes del login.
    path('branding/', BrandingView.as_view(), name='branding'),
    # Editable: solo administradores.
    path('branding/settings/', BrandingAdminView.as_view(), name='branding-settings'),
    # El logotipo va aparte: viaja como archivo, no como JSON.
    path('branding/settings/logo/', BrandingLogoView.as_view(), name='branding-logo'),
    # Acceso propio. Mismas rutas que el IAM para que el frontend no cambie
    # el día de la integración.
    path('auth/', include('api.v1.auth.urls')),
    # Roles y permisos del módulo.
    path('roles/', include('api.v1.roles.urls')),
    # Proyecto de Emprendimiento — subproceso de Vinculación con la Sociedad.
    path('entrepreneurship/', include('api.v1.entrepreneurship.urls')),
]
