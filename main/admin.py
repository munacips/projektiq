from django.contrib import admin
from .models import Account, Project, Organization, Issue, ProjectRequirement, ChangeRequest, AccountOrganization, AccountProject, IssueComment, ProjectTask, ToDo, Conversation, ConversationMessage, ConversationAttachment

class AccountAdmin(admin.ModelAdmin):
    search_fields = ['email']

admin.site.register(Account, AccountAdmin)
admin.site.register([Project, Organization, Issue, ProjectRequirement, ChangeRequest, AccountOrganization, AccountProject, IssueComment, ProjectTask, ToDo, Conversation, ConversationMessage, ConversationAttachment])