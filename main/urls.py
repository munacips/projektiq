from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('projects/<int:id>', views.projects,name='projects'),
    path('project/<int:id>', views.project,name='project'),
    path('organizations/', views.organizations,name='organizations'),
    path('organizations/<int:id>', views.organization,name='organization'),
    path('organizations/<int:id>/issues/', views.organization_issues,name='organization_issues'),
    path('issues/<int:id>', views.issue,name='issue'),
    path('projects/<int:id>/issues/', views.project_issues,name='project_issues'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)