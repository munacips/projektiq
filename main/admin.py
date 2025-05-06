from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Account, Project, Organization, Issue, ProjectRequirement, ChangeRequest, AccountOrganization, AccountProject, IssueComment, ProjectTask, ToDo, Conversation, ConversationMessage, ConversationAttachment, ChangeRequestComment, TimeLog, ProjectComment, ProjectHistory

class AccountAdmin(admin.ModelAdmin):
    search_fields = ['email']

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(Account, AccountAdmin)
admin.site.register([Project,ChangeRequestComment, Organization, Issue, ProjectRequirement, ChangeRequest, AccountOrganization, AccountProject, IssueComment, ProjectTask, ToDo, Conversation, ConversationMessage, ConversationAttachment, TimeLog, ProjectComment, ProjectHistory])