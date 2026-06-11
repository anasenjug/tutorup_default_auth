from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Avg

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
    first_name = models.CharField(max_length=50, blank = True, null = True)
    last_name = models.CharField(max_length = 100, blank = True, null = True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    is_in_person = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    subjects = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    availability = models.TextField(blank=True, null=True)
    works_at = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="tutor_profiles/", 
        default="tutor_profiles/default.png",
        )
    is_featured = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg,1) if avg else 0
    
    @property
    def review_count(self):
        return self.reviews.count()

class Review(models.Model):
    tutor = models.ForeignKey(TutorProfile,on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_reviews")
    rating = models.PositiveIntegerField()  # Assuming a scale of 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student.user.username} for {self.tutor.user.username}"
    
class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    EDUCATION_CHOICES = [
        ('middle_school','Middle School'),
        ('high_school','High School'),
        ('college', 'College'),
        ('graduate_school', 'Graduate School'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_sent')
    tutor_profile = models.ForeignKey('TutorProfile', on_delete=models.CASCADE, related_name='bookings_received')

    description = models.TextField()
    education_level = models.CharField(max_length=30, choices = EDUCATION_CHOICES)
    rate_at_booking = models.DecimalField(max_digits=6, decimal_places=2)

    status = models.CharField(max_length = 15, choices = STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking from {self.student.username} to Tutor {self.tutor_profile.user.username} ({self.status})" 
