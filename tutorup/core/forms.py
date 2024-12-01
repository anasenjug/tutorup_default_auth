from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *  # Or User model if using the default model

class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'  # Set user type to student
        if commit:
            user.save()
        return user

class TutorRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'tutor'  # Set user type to user
        user.is_active = False  # Account needs admin approval
        if commit:
            user.save()
        return user
    
class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = [
            'location', 'is_online', 'is_in_person', 'hourly_rate',
            'about_me', 'subjects', 'qualifications', 'availability', 'profile_picture'
        ]
        widgets = {
            'about_me': forms.Textarea(attrs={'rows': 4}),
            'availability': forms.Textarea(attrs={'rows': 2}),
        }