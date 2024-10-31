from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Project, Organization, Account, Issue
from .serializers import ProjectSerializer, OrganizationSerializer, AccountSerializer, IssueSerializer


@api_view(['GET','POST'])
#@permission_classes([IsAuthenticated])
def projects(request,id):
    try:
        organization = Organization.objects.get(id=id)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        projects = Project.objects.filter(organizations=organization)
        serializer = ProjectSerializer(projects,many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','POST'])
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
#@permission_classes([IsAuthenticated])
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
