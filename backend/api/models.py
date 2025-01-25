from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    patient_id = models.CharField(max_length=50, unique=True)

class Message(models.Model):
    CHANNEL_CHOICES = (
        ('patients', "Patients"),
        ('employees', "Employees"),
    )
    content = models.CharField(max_length=500)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="received_messages")
    channel = models.TextField(max_length=15, choices=CHANNEL_CHOICES)