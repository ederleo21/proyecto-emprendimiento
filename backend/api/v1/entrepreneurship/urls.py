from django.urls import path

from api.v1.entrepreneurship import views as v

urlpatterns = [
    path('stages/', v.StageListView.as_view(), name='ent-stage-list'),
    path('metrics/', v.StageMetricsView.as_view(), name='ent-metrics'),
    path('projects/', v.ProjectListCreateView.as_view(), name='ent-project-list'),
    path('projects/<uuid:pk>/', v.ProjectDetailView.as_view(), name='ent-project-detail'),
    path(
        'projects/<uuid:pk>/activities/<uuid:activity_id>/',
        v.ProjectActivityToggleView.as_view(), name='ent-project-activity',
    ),
]
