from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('projects/', views.projects,name='projects'),
    path('project/<int:id>', views.project,name='project'),

    path('organizations/', views.organizations,name='organizations'),
    path('organizations/<int:id>', views.organization,name='organization'),
    path('organizations/<int:id>/issues/', views.organization_issues,name='organization_issues'),
    path('organizations/<int:id>/change_requests/', views.organization_change_requests,name='organization_change_requests'),

    path('issues/<int:id>', views.issue,name='issue'),
    path('post_issue/<int:id>',views.post_issue_comment,name="post_issue"),
    path('get_issue_comments/<int:id>',views.get_issue_comments,name="get_issue_comments"),

    path('projects/<int:id>/issues/', views.project_issues,name='project_issues'),
    path('projects/<int:id>/requirements/', views.project_requirements,name='project_requirements'),
    path('project/<int:id>/requirements/', views.project_requirement,name='project_requirement'),
    path('projects/<int:id>/change_requests/', views.project_change_requests,name='project_change_requests'),

    path('change_request/<int:id>',views.change_request,name='change_request'),

    path('my_projects/', views.my_projects,name='my_projects'),
    path('my_organizations/', views.my_organizations,name='my_organizations'),
    path('my_linked_organizations/',views.my_linked_organizations,name="my_linked_organizations"),
    path('my_tasks/', views.my_tasks,name='my_tasks'),
    path('my_overdue_tasks/',views.my_overdue_tasks,name="my_overdue_tasks"),
    path('my_issues/', views.my_issues,name='my_issues'),
    path('my_schedule/',views.my_schedule,name="my_schedule"),
    path('my_conversations/',views.my_conversations,name="my_conversations"),
    path('user_project_summary/',views.user_project_summary,name="user_project_summary"),
    path('send_message/',views.send_message,name="send_message"),

    path('test/',views.check_authentication,name='test'),

    path('search/',views.search,name='search'),

    path('messages/<int:id>/',views.mark_messages_as_read,name='message'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)