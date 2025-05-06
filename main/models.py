from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.core.exceptions import ValidationError


STATUS_CHOICES = [
        ('Requirements', 'Requirements'),
        ('Design', 'Design'),
        ('Development', 'Development'),
        ('Testing', 'Testing'),
        ('Deployment', 'Deployment'),
        ('Maintenance', 'Maintenance'),
        ('Closed', 'Closed'),
        ('Cancelled', 'Cancelled'),
        ('Other', 'Other'),
    ]

ROLES = [
        ('General Manager', 'General Manager'),
        ('Admin', 'Admin'),
        ('Developer', 'Developer'),
        ('Tester', 'Tester'),
        ('Maintainer', 'Maintainer'),
        ('Member', 'Member'),
]

PRIORITIES = [
    ('low','Low'),
    ('medium', 'Medium'),
    ('high','High'),
    ('very high', 'Very High')
]

class Account(AbstractUser):

    phone_number = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Organization(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField(null=True, blank=True)
    active_projects = models.IntegerField(null=True, blank=True)
    total_members = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.active_projects = Project.objects.filter(organizations=self).count()
        self.total_members = AccountOrganization.objects.filter(organization=self).count()
        super().save(*args, **kwargs)


class AccountOrganization(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=100, choices=ROLES, default='Member')
    approved = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.organization.name + ' : ' + self.account.username


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Account, on_delete=models.CASCADE)
    organizations = models.ManyToManyField(Organization, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Requirements')
    deadline = models.DateTimeField(null=True, blank=True)
    completion_percentage = models.IntegerField(null=True, blank=True,default=0)
    stage_due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def calculate_stage_status(self):
        if not self.stage_due_date:
            return "Unknown"  # Default for missing due dates
        days_left = (self.stage_due_date - now()).days
        if days_left >= 7:
            return "On Track"
        elif 0 <= days_left < 7:
            return "At Risk"
        else:
            return "Delayed"

    class Meta:
        ordering = ['-date_created']


class ProjectComment(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class ProjectTask(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE,null=True,blank=True)
    task = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    implemented = models.BooleanField(default=False)
    hours_needed = models.IntegerField(null=True, blank=True)
    priority = models.CharField(max_length=255,null=True,blank=True,choices=PRIORITIES,default='Medium')
    assigned_to = models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True,related_name='tasks_assigned_to')
    assigned_by = models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True,related_name='tasks_assigned_by')

    def __str__(self):
        return self.task


class AccountProject(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=100, choices=ROLES, default='Member')

    def __str__(self):
        return self.project.name + ' : ' + self.account.username


class ProjectHistory(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    description = models.TextField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Requirements')


class Issue(models.Model):
    issue = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='issues_assigned_to')
    attendants = models.ManyToManyField(Account, blank=True, related_name='issues_as_attendant')
    due_date = models.DateTimeField(blank=True, null=True)
    assigned_by = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='issues_assigned_by')
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.issue

    class Meta:
        ordering = ['-date_created']


class ProjectRequirement(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    requirement = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    implemented = models.BooleanField(default=False)

    def __str__(self): 
        return self.requirement

    class Meta:
        ordering = ['-date_created']


class ChangeRequest(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    request = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    implemented = models.BooleanField(default=False)

    def __str__(self):
        return self.request
    
    class Meta:
        ordering = ['-date_created']


class IssueComment(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def clean(self):
        # Ensure that issue is null if parent is not null
        if self.parent and self.issue is not None:
            raise ValidationError("Issue must be null when a parent is set.")
        
        # Ensure that parent is null if issue is not null
        if self.issue and self.parent is not None:
            raise ValidationError("Parent must be null when an issue is set.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ['-date_created']


class ToDo(models.Model):
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE,null=True,blank=True)
    issue = models.ForeignKey(Issue,on_delete=models.CASCADE,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def clean(self):
        
        # Ensure that task and issue are not set at the same time
        if self.task and self.issue:
            raise ValidationError("Task and issue cannot be set at the same time.")

    def __str__(self):
        return self.description


class Conversation(models.Model):
    description = models.TextField(blank=True,null=True)
    subject = models.CharField(max_length=255,blank=True,null=True)
    participants = models.ManyToManyField(Account, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    def clean(self):
        super().clean()
        # We can only validate this after the instance is saved and participants are added
        # So this validation will be called in a custom save method for the M2M relationship

    def save(self, *args, **kwargs):
        # First save the model to get an ID if it's new
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-date_created']
        # We can't add constraints here directly since we need to check after M2M is populated


# Create a custom through model for the M2M relationship
class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('conversation', 'account')


class ConversationMessage(models.Model):
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name="messages")
    sent_by = models.ForeignKey(Account,on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['-date_created']


class ConversationAttachment(models.Model):
    description = models.TextField()
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='attachments/')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.attachment.name

    class Meta:
        ordering = ['-date_created']

class ChangeRequestComment(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def clean(self):
        # Ensure that change_request is null if parent is not null
        if self.parent and self.change_request is not None:
            raise ValidationError("Change request must be null when a parent is set.")
        
        # Ensure that parent is null if change_request is not null
        if self.change_request and self.parent is not None:
            raise ValidationError("Parent must be null when a change request is set.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ['-date_created']


class TimeLog(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    task = models.ForeignKey(ProjectTask,on_delete=models.CASCADE,null=True,blank=True)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hours_spent = models.IntegerField(null=True, blank=True)
    billable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            time_diff = self.end_time - self.start_time
            self.hours_spent = round(time_diff.total_seconds() / 3600)
        
        super().save(*args, **kwargs)


from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError

@receiver(m2m_changed, sender=Conversation.participants.through)
def validate_unique_two_person_conversation(sender, instance, action, **kwargs):
    if action == 'post_add':
        participants = instance.participants.all()
        participant_count = participants.count()
        
        # Only apply the constraint for exactly 2 participants
        if participant_count == 2:
            participant_ids = sorted(participants.values_list('id', flat=True))
            
            # Check if there's another conversation with these exact 2 participants
            duplicate_conversations = Conversation.objects.filter(
                participants__in=participant_ids
            ).annotate(
                participant_count=models.Count('participants')
            ).filter(
                participant_count=2
            ).exclude(
                id=instance.id
            )
            
            # For each potential duplicate, check if it has exactly these two participants
            for conv in duplicate_conversations:
                conv_participant_ids = sorted(conv.participants.values_list('id', flat=True))
                if conv_participant_ids == participant_ids:
                    raise ValidationError(
                        "A conversation between these two participants already exists."
                    )
