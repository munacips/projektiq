from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Account, Organization, Issue, ProjectRequirement,ChangeRequest, ProjectHistory, Account, IssueComment, AccountProject, AccountOrganization, ProjectTask, ToDo, Conversation, ConversationAttachment, ConversationMessage



class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = IssueCommentSerializer(instance, context=self.context)
        return serializer.data


class IssueCommentSerializer(ModelSerializer):
    children = RecursiveCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = IssueComment
        fields = ['id', 'parent', 'issue', 'user', 'comment', 
                 'date_created', 'date_updated', 'children']
        depth = 1

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Only include children if they exist
        children = instance.issuecomment_set.all()
        if not children:
            representation.pop('children', None)
            
        return representation


class IssueSerializer(serializers.ModelSerializer):
    attendants_names = serializers.SerializerMethodField()
    assigned_to_name = serializers.CharField(source="assigned_to.username", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.username", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    comments = IssueCommentSerializer(many=True, read_only=True, source="issuecomment_set")

    class Meta:
        model = Issue
        fields = [
            'id', 'issue', 'description', 'project', 'project_name', 
            'date_created', 'date_updated', 'assigned_to', 'assigned_to_name', 
            'attendants', 'attendants_names', 'due_date', 'assigned_by', 
            'assigned_by_name', 'closed', 'comments'
        ]


    def get_attendants_names(self, obj):
        return [user.username for user in obj.attendants.all()]


class ProjectRequirementSerializer(ModelSerializer):
    class Meta:
        model = ProjectRequirement
        fields = '__all__'


class ChangeRequestSerializer(ModelSerializer):
    class Meta:
        model = ChangeRequest
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    organization_names = serializers.SerializerMethodField()
    issues = IssueSerializer(many=True, read_only=True, source='issue_set')
    requirements = ProjectRequirementSerializer(many=True, read_only=True, source="projectrequirement_set")
    change_requests = ChangeRequestSerializer(many=True, read_only=True, source="changerequest_set")
    project_manager = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'date_created', 'date_updated', 
                  'manager', 'status', 'organization_names', 'issues', 'members','requirements','change_requests','project_manager','deadline','stage_due_date','organizations','completion_percentage']

    def get_organization_names(self, obj):
        return [org.name for org in obj.organizations.all()]

    def get_project_manager(self, obj):
        return obj.manager.username

    def get_members(self,obj):
        account_projects = AccountProject.objects.filter(project=obj)
        return AccountProjectSerializer(account_projects,many=True).data
        # accounts = [account.account for account in account_projects]
        # return AccountSerializer(accounts, many=True).data


class OrganizationSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'rating', 'active_projects', 'total_members', 'projects','members']

    def get_projects(self, obj):
        projects = obj.project_set.all()
        return ProjectSerializer(projects, many=True).data

    def get_members(self, obj):
            account_organizations = AccountOrganization.objects.filter(organization=obj)
            return AccountOrganizationSerializer(account_organizations, many=True).data


class ProjectHistorySerializer(ModelSerializer):
    class Meta:
        model = ProjectHistory
        fields = '__all__'


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class AccountProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='project.id')
    project_name = serializers.CharField(source='project.name')
    project_description = serializers.CharField(source='project.description')
    project_status = serializers.CharField(source='project.status')
    project_deadline = serializers.DateTimeField(source='project.deadline')
    completion_percentage = serializers.IntegerField(source='project.completion_percentage')
    project_manager = serializers.CharField(source='project.manager.username')
    organization_names = serializers.SerializerMethodField()
    active_members = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    username = serializers.CharField(source='account.username')
    account_id = serializers.IntegerField(source='account.id')


    class Meta:
        model = AccountProject
        fields = ['username','account_id','id','project_name', 'date_created', 'project_description', 'members', 'project_status', 'organization_names', 'role', 'date_created', 'date_updated', 'project_deadline', 'completion_percentage', 'project_manager','active_members']

    def get_active_members(self, obj):
        # Count all AccountProject objects associated with the same project
        return AccountProject.objects.filter(project=obj.project).count()

    def get_organization_names(self, obj):
        return [org.name for org in obj.project.organizations.all()]

    def get_members(self, obj):
            account_organizations = AccountOrganization.objects.filter(organization=obj.project.organizations.first())
            return AccountOrganizationSerializer(account_organizations, many=True).data


class AccountOrganizationSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.username', read_only=True)
    total_members = serializers.IntegerField(source='organization.total_members', read_only=True)
    active_projects = serializers.IntegerField(source='organization.active_projects', read_only=True)
    rating = serializers.IntegerField(source='organization.rating', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_description = serializers.CharField(source='organization.description', read_only=True)

    class Meta:
        model = AccountOrganization
        fields = [
            'id',
            'total_members',
            'active_projects',
            'rating',
            'account_name', 
            'organization_name', 
            'organization_description', 
            'date_created', 
            'date_updated', 
            'role'
        ]


class ProjectTaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = ProjectTask
        fields = [
            'id',
            'task',
            'description',
            'date_created',
            'date_updated',
            'due_date',
            'implemented',
            'assigned_to',
            'assigned_by'
        ]


class ToDoSerializer(serializers.ModelSerializer):
    issue_name = serializers.SerializerMethodField()
    task_name = serializers.SerializerMethodField()

    class Meta:
        model = ToDo
        fields = [
            'id',
            'description',
            'task',
            'task_name',
            'issue',
            'issue_name',
            'date_created',
            'date_updated',
            'date_start',
            'date_end',
            'completed'
        ]

    def get_issue_name(self, obj):
        if obj.issue:
            return obj.issue.issue  # Assuming the 'Issue' model has a 'name' field
        return None

    def get_task_name(self, obj):
        if obj.task:
            return obj.task.task  # Assuming the 'ProjectTask' model has a 'name' field
        return None


class ConversationMessageSerializer(serializers.ModelSerializer):
    sent_by_username = serializers.SerializerMethodField()

    class Meta:
        model = ConversationMessage
        fields = [
            'id',
            'conversation',
            'sent_by',
            'message',
            'date_created',
            'date_updated',
            'sent_by_username',
            'is_read'
        ]
    
    def get_sent_by_username(self, obj):
        return obj.sent_by.username


class ConversationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationAttachment
        fields = [
            'id',
            'conversation',
            'sent_by',
            'attachment',
            'date_created',
            'date_updated'
        ]


class ConversationSerializer(serializers.ModelSerializer):
    participants_usernames = serializers.SerializerMethodField()
    messages = ConversationMessageSerializer(many=True, read_only=True)
    attachments = ConversationAttachmentSerializer(many=True, read_only=True)
    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'description',
            'subject',
            'participants',
            'participants_usernames',
            'messages',
            'attachments',
            'unread_messages',
            'date_created',
            'date_updated',
        ]

    def get_participants_usernames(self, obj):
        return [user.username for user in obj.participants.all()]

    def get_unread_messages(self, obj):
        current_user = self.context['request'].user.id
        unread_messages = obj.messages.filter(is_read=False).exclude(sent_by=current_user)
        return unread_messages.count()


class AccountOrganizationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='account.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = AccountOrganization
        fields = ['id','username', 'organization_name', 'role', 'date_created', 'date_updated','account','organization','approved','admin_approved']