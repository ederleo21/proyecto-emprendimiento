"""Rutas raíz.

El prefijo `/api/` se deja explícito para que, al montarlo detrás del gateway
de InnoTech como `/outreach/`, las URLs queden
`/outreach/api/v1/...` — el mismo formato que el resto de servicios.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView,
)

urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Los archivos subidos —hoy solo el logotipo— los sirve Django en desarrollo.
# En producción eso lo hace el servidor web de adelante, y por eso va detrás
# del `DEBUG`.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
