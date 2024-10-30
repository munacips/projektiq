from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):

    phone_number = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Organization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Account,on_delete=models.CASCADE)
    organizations = models.ManyToManyField(Organization,blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-date_created']