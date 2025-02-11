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
        user.user_type = 'tutor'  # Set user type to tutor
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

class TutorSearchForm(forms.Form):
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Subject...'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Location...'}))
    is_online = forms.BooleanField(required=False, label="Online", widget=forms.CheckboxInput)
    is_in_person = forms.BooleanField(required=False, label="In-person", widget=forms.CheckboxInput)
    min_price = forms.DecimalField(required=False, max_digits=6, decimal_places=2, label="Min Price")
    max_price = forms.DecimalField(required=False, max_digits=6, decimal_places=2, label="Max Price")
    # todo: ratings = forms.IntegerField(required=False, label="Min Rating", widget=forms.NumberInput(attrs={'min': 1, 'max': 5}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }