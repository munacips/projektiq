from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Account, Organization


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


# class ConversationSerializer(serializers.ModelSerializer):
#     participants_usernames = serializers.SerializerMethodField()

#     class Meta:
#         model = Conversation
#         fields = '__all__'  # Include all fields from the Conversation model

#     def get_participants_usernames(self, obj):
#         # Assuming 'participants' is a ManyToManyField or a related field
#         return [user.username for user in obj.participants.all()]