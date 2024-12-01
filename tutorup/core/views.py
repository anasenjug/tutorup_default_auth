from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from .utils import *
from django.contrib.auth import logout, get_user_model
from django.http import Http404

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save student user immediately
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})


def tutor_register(request):
    if request.method == 'POST':
        form = TutorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save tutor but set is_active to False (awaiting admin approval)
    else:
        form = TutorRegistrationForm()

    return render(request, 'register_tutor.html', {'form': form})

def index(request):
    return render(request,'index.html')


@tutor_required
@login_required
def tutor_profile_edit(request):
    if request.user.user_type != 'tutor':
        return redirect('index')  # Redirect if not a tutor

    profile, created = TutorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TutorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('tutor_profile_view')  # Replace with the actual view name
    else:
        form = TutorProfileForm(instance=profile)

    return render(request, 'tutor_profile_edit.html', {'form': form})


@login_required
def tutor_profile_view(request, pk):
    # Get the user
    user = get_object_or_404(get_user_model(), pk=pk, user_type='tutor')

    # Get or create the TutorProfile
    tutor_profile, created = TutorProfile.objects.get_or_create(user=user)

    if created:
        # If the profile was created, you can set default values or redirect if necessary
        tutor_profile.save()

    context = {
        'tutor_profile': tutor_profile,
    }
    return render(request, 'tutor_profile_view.html', context)
