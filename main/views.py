from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Project, Organization, Account, Issue,  ProjectRequirement, ChangeRequest, ProjectHistory, AccountOrganization, AccountProject, IssueComment, ProjectTask, ToDo, Conversation, ConversationMessage, AccountOrganization
from .serializers import ProjectSerializer, AccountSerializer, IssueSerializer, ProjectRequirementSerializer, ChangeRequestSerializer, ProjectHistorySerializer, AccountSerializer, AccountProjectSerializer, IssueCommentSerializer, AccountOrganizationSerializer, ProjectTaskSerializer, OrganizationSerializer, ToDoSerializer, ConversationSerializer, ConversationMessageSerializer, AccountOrganizationSerializer
from django.utils.timezone import now, timedelta
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404

import logging

logger = logging.getLogger(__name__)

next_seven_days = now() + timedelta(days=7)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def projects(request):
    if request.method == "GET":
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = request.data.copy()
        print('Data : ', data)
        manager_id = data.get('manager')
        if manager_id:
            try:
                manager = Account.objects.get(username=manager_id)
                data['manager'] = manager.id
                data['organizations'] = data['participantOrganizations']
            except Account.DoesNotExist:
                return Response(
                    {'error': 'Invalid manager ID'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            project = serializer.save()
            AccountProject.objects.get_or_create(
                account=manager, 
                project=project,
                role='General Manager'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def organizations(request):
    if request.method == "GET":
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def organization(request,id):
    try:
        organization = Organization.objects.get(id=id)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = OrganizationSerializer(organization,data=request.data)
        if serializer.is_valid():
            return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def project(request,id):
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProjectSerializer(project,data=request.data)
        if serializer.is_valid():
            return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def issues(request):
    if request.method == "GET":
        issues = Issue.objects.all()
        serializer = IssueSerializer(issues,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        print("Error : ",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def project_issues(request,id):
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        issues = Issue.objects.filter(project=project)
        serializer = IssueSerializer(issues,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def issue(request,id):
    try:
        issue = Issue.objects.get(id=id)
    except Issue.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = IssueSerializer(issue)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = IssueSerializer(issue,data=request.data)
        if serializer.is_valid():            
            return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def organization_issues(request,id):
    try:
        organization = Organization.objects.get(id=id)
        projects = Project.objects.filter(organizations=organization)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        issues = Issue.objects.filter(project__in=projects)
        serializer = IssueSerializer(issues,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def project_requirements(request,id):
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        requirements = ProjectRequirement.objects.filter(project=project)
        serializer = ProjectRequirementSerializer(requirements,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProjectRequirementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def project_requirement(request,id):
    try:
        project_requirement = ProjectRequirement.objects.get(id=id)
    except ProjectRequirement.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProjectRequirementSerializer(project_requirement)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProjectRequirementSerializer(project_requirement,data=request.data)
        if serializer.is_valid():
            serializer.save()

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def project_change_requests(request,id):
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        change_requests = ChangeRequest.objects.filter(project=project)
        serializer = ChangeRequestSerializer(change_requests,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ChangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def organization_change_requests(request,id):
    try:
        organization = Organization.objects.get(id=id)
        projects = Project.objects.filter(organizations=organization)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        change_requests = ChangeRequest.objects.filter(project__in=projects)
        serializer = ChangeRequestSerializer(change_requests,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ChangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def change_requests(request):
    if request.method == "GET":
        change_requests = ChangeRequest.objects.all()
        serializer = ChangeRequestSerializer(change_requests,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ChangeRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        print("Data : ",request.data)
        print("Error : ",serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def change_request(request,id):
    try:
        change_request = ChangeRequest.objects.get(id=id)
    except ChangeRequest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ChangeRequestSerializer(change_request)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ChangeRequestSerializer(change_request,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def project_history(request,id):
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        history = ProjectHistory.objects.filter(project=project)
        serializer = ProjectHistorySerializer(history,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProjectHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_projects(request):
    if request.method == "GET":
        try:
            account = Account.objects.get(id=request.user.id)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        projects = AccountProject.objects.filter(account=account)
        serializer = AccountProjectSerializer(projects,many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_organizations(request):
    if request.method == "GET":
        try:
            account = Account.objects.get(id=request.user.id)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        organizations = AccountOrganization.objects.filter(account=account)
        serializer = AccountOrganizationSerializer(organizations,many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_linked_organizations(request):
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    linked_organizations = Organization.objects.filter(accountorganization__account=user)
    serializer = OrganizationSerializer(linked_organizations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_issue_comment(request,id):
    if request.method == "POST":
        try:
            account = Account.objects.get(id=request.user.id)
        except Account.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            issue = Issue.objects.get(id=id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = request.data
        comment = IssueComment(issue=issue, user=account, comment=data['comment'])
        comment.save()
        serializer = IssueCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_issue_comments(request,id):
    if request.method == 'GET':
        try:
            issue = Issue.objects.get(id=id)
        except Issue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comments = IssueComment.objects.filter(issue=issue)
        serializer = IssueCommentSerializer(comments,many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_authentication(request):
    return Response(status=status.HTTP_200_OK)


@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def my_tasks(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        tasks = ProjectTask.objects.filter(assigned_to=account)
        serializer = ProjectTaskSerializer(tasks,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        task = ProjectTask(task=data['task'], description=data['description'], assigned_to=account)
        task.save()
        serializer = ProjectTaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'PUT':
        data = request.data
        print("The Data : ",data)
        task = ProjectTask.objects.get(id=data['id'])
        task.implemented = True
        task.save()
        serializer = ProjectTaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_overdue_tasks(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        tasks = ProjectTask.objects.filter(assigned_to=account, due_date__lte=timezone.now())
        serializer = ProjectTaskSerializer(tasks,many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_project_summary(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    total_tasks = ProjectTask.objects.filter(assigned_to=account,implemented=False).count()

    # Overdue tasks count
    overdue_tasks_count = ProjectTask.objects.filter(
        assigned_to=account,
        due_date__lt=now(),
        implemented=False
    ).count()

    # Total Issues
    issues_count = Issue.objects.filter(attendants=account,closed=False).count()

    # Overdue Issues count
    overdue_issues_count = Issue.objects.filter(
        attendants=account,
        due_date__lt=now(),
        closed=False
    ).count()

    # Issues due in the next 7 days count
    upcoming_issues_count = Issue.objects.filter(
        attendants=account,
        due_date__range=[now(), next_seven_days],
        closed=False
    ).count()

    # Tasks due in the next 7 days count
    upcoming_tasks_count = ProjectTask.objects.filter(
        assigned_to=account,
        due_date__range=[now(), next_seven_days],
        implemented=False
    ).count()

    # Total number of projects the user is involved in
    involved_projects = Project.objects.filter(organizations__accountorganization__account=account).distinct()
    total_projects = involved_projects.count()

    # Projects by calculated stage status
    projects_status = {
        "on_track": 0,
        "at_risk": 0,
        "delayed": 0,
    }
    for project in involved_projects:
        stage_status = project.calculate_stage_status()
        if stage_status == "On Track":
            projects_status["on_track"] += 1
        elif stage_status == "At Risk":
            projects_status["at_risk"] += 1
        elif stage_status == "Delayed":
            projects_status["delayed"] += 1

    # Construct the response
    response_data = {
        'overdue_tasks_count': overdue_tasks_count,
        'upcoming_tasks_count': upcoming_tasks_count,
        'total_projects': total_projects,
        'total_tasks' : total_tasks,
        'projects_by_status': projects_status,
        'issues_count': issues_count,
        'overdue_issues_count': overdue_issues_count,
        'upcoming_issues_count': upcoming_issues_count,
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    search_query = request.GET.get('query')
    if search_query:
        search_query = search_query.lower()
        
        projects = Project.objects.filter(name__icontains=search_query)
        issues = Issue.objects.filter(issue__icontains=search_query)
        change_requests = ChangeRequest.objects.filter(request__icontains=search_query)  # Make sure `request` is the correct field.
        organizations = Organization.objects.filter(name__icontains=search_query)

        results = []
        for project in projects:
            results.append({'type': 'Project', 'name': project.name, 'id': project.id})
        for issue in issues:
            results.append({'type': 'Issue', 'title': issue.issue,  'id': issue.id})
        for change_request in change_requests:
            results.append({'type': 'Change Request', 'title': change_request.request, 'id' : change_request.id})  # Update if needed.
        for organization in organizations:
            results.append({'type': 'Organization', 'name': organization.name})

        return Response(results)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET','PUT'])
@permission_classes([IsAuthenticated])
def my_issues(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        issues = Issue.objects.filter(attendants=account)
        issues.union(Issue.objects.filter(assigned_to=account))
        serializer = IssueSerializer(issues,many=True)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = request.data
        issue = Issue.objects.get(id=data['id'])
        issue.closed = True
        issue.save()
        serializer = IssueSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET','POST','PUT'])
@permission_classes([IsAuthenticated])
def my_schedule(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        tasks = ProjectTask.objects.filter(assigned_to=account)
        serializer = ProjectTaskSerializer(tasks,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # data = request.data
        # todo = ToDo(description=data['description'],date_start=data['date_start'],date_end=data['date_end'])
        # todo.save()
        # serializer = ToDoSerializer(todo)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        pass
    elif request.method == 'PUT':
        # data = request.data
        # todo = ToDo.objects.get(id=data['id'])
        # todo.completed = True
        # todo.save()
        # serializer = ToDoSerializer(todo)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        pass


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_conversations(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        logger.error(f"Account with id {request.user.id} does not exist.")
        return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        logger.info(f"Fetching conversations for account {account.id}")
        conversations = Conversation.objects.filter(participants=account)
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})

        return Response(serializer.data)

    elif request.method == 'POST':
        
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Conversation creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_message(request):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        data =  {
            "conversation" : request.data.get('chat'),
            "sent_by" : account.id,
            "message" : request.data.get('message')
        }
        serializer = ConversationMessageSerializer(data=data)
        if serializer.is_valid():
            message = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Message creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mark_messages_as_read(request,id):
    try:
        account = Account.objects.get(id=request.user.id)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        messages = Message.objects.filter(account=account)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if id:
            try:
                message = ConversationMessage.objects.get(id=id)
            except ConversationMessage.DoesNotExist:
                return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
            
            data = request.data
            is_read = data.get('is_read', None)

            if is_read is None:
                return Response({"error": "'is_read' field is required."}, status=status.HTTP_400_BAD_REQUEST)

            message.is_read = is_read
            message.save()
            serializer = ConversationMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            data = request.data
            message_ids = data.get('message_ids', [])
            if not message_ids:
                return Response({"error": "'message_ids' field is required."}, status=status.HTTP_400_BAD_REQUEST)

            updated_count = Message.objects.filter(id__in=message_ids, account=account).update(is_read=True)
            return Response(
                {"message": f"{updated_count} messages marked as read."},
                status=status.HTTP_200_OK,
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_to_organization(request):
    try:
        org_id = request.data.get('org_id')
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        # First check if organization and account exist
        organization = Organization.objects.get(id=org_id)
        account = Account.objects.get(id=user_id)
        
        # Check if the membership already exists
        existing_membership = AccountOrganization.objects.filter(
            organization=organization,
            account=account
        ).exists()
        
        if existing_membership:
            return Response(
                {"detail": "User is already a member of this organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If no existing membership, create new one
        AccountOrganization.objects.create(
            organization=organization,
            account=account,
            role=role
        )
        
        return Response(
            {"detail": "Member added successfully"},
            status=status.HTTP_201_CREATED
        )
        
    except Organization.DoesNotExist:
        return Response(
            {"detail": "Organization not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Account.DoesNotExist:
        return Response(
            {"detail": "Account not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member_from_organization(request):
    try:
        org_id = request.data.get('org_id')
        user_id = request.data.get('user_id')

        # First check if organization and account exist
        organization = Organization.objects.get(id=org_id)
        account_org = AccountOrganization.objects.get(id=user_id)

        account_org.delete()

        return Response(
            {"detail": "Member removed successfully"},
            status=status.HTTP_200_OK
        )
    except Organization.DoesNotExist:
        return Response(
            {"detail": "Organization not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Account.DoesNotExist:
        return Response(
            {"detail": "Account not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.GET.get('query', '')
    if not query:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    users = Account.objects.filter(username__icontains=query)
    serializer = AccountSerializer(users, many=True)
    return Response(serializer.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_member_role(request):
    try:
        org_id = request.data.get('org_id')
        user_id = request.data.get('user_id')
        role = request.data.get('role')

        # First check if organization and account exist
        print(f"User ID: {user_id}, Type: {type(user_id)}")
        print(f"Accounts in DB: {list(Account.objects.values_list('id', flat=True))}")
        organization = Organization.objects.get(id=org_id)
        acc_org = AccountOrganization.objects.get(id=user_id)

        acc_org.role = role
        acc_org.save()

        return Response(
            {"detail": "Member role updated successfully"},
            status=status.HTTP_200_OK
        )
    except Organization.DoesNotExist:
        return Response(
            {"detail": "Organization not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Account.DoesNotExist:
        return Response(
            {"detail": "Account not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )