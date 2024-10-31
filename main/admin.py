from django.contrib import admin
from .models import Account, Project, Organization, Issue

class AccountAdmin(admin.ModelAdmin):
    search_fields = ['email']

admin.site.register(Account, AccountAdmin)
admin.site.register([Project, Organization, Issue])