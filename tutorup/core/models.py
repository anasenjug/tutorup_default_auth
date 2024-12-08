from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.username
    
class TutorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_profile")
    location = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    is_in_person = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    subjects = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    availability = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="tutor_profiles/", 
        default="tutor_profiles/default.png",
        )
    is_featured = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.user.username}'s Profile"