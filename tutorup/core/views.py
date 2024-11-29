from django.shortcuts import render, redirect
from .forms import StudentRegistrationForm
from .forms import UserRegistrationForm

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save student user immediately
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})


def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save user but set is_active to False (awaiting admin approval)
    else:
        form = UserRegistrationForm()

    return render(request, 'register_user.html', {'form': form})

def index(request):
    return render(request,'index.html')