from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Or User model if using the default model

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

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'user'  # Set user type to user
        user.is_active = False  # Account needs admin approval
        if commit:
            user.save()
        return user