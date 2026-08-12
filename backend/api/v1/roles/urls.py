from django.urls import path

from api.v1.roles import views as v

urlpatterns = [
    # Antes que el detalle: si no, "permissions" se leería como un id.
    path('permissions/', v.PermissionCatalogView.as_view(), name='role-permissions'),
    path('', v.RoleListCreateView.as_view(), name='role-list'),
    path('<uuid:pk>/', v.RoleDetailView.as_view(), name='role-detail'),
]
