from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from .utils import *
from django.contrib.auth import logout, get_user_model
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': 'Registration successful!'}, status=200)
        return render(request, 'partials/registration_errors.html', {'form': form}, status=400)

    # Render form as a partial for htmx
    form = StudentRegistrationForm()
    return render(request, 'partials/register_student_form.html', {'form': form})


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
            return redirect('tutor_profile_view', pk=request.user.id)
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

@login_required
def tutor_search(request):
    # Create an initial query set of all tutors
    tutors = TutorProfile.objects.all()

    # Handle search query parameter for general search (across multiple fields)
    query = request.GET.get('q', None)

    if query:
        tutors = tutors.filter(
            Q(user__username__icontains=query) |  # Search tutor username
            Q(subjects__icontains=query) |  # Search subjects
            Q(location__icontains=query) |  # Search location
            Q(about_me__icontains=query)  # Search about me
        )

    # Apply additional filters (subject, location, online, etc.)
    subject = request.GET.get('subject', None)
    if subject:
        tutors = tutors.filter(subjects__icontains=subject)

    location = request.GET.get('location', None)
    if location:
        tutors = tutors.filter(location__icontains=location)

    is_online = request.GET.get('is_online', None)
    if is_online:
        tutors = tutors.filter(is_online=True)

    is_in_person = request.GET.get('is_in_person', None)
    if is_in_person:
        tutors = tutors.filter(is_in_person=True)

    min_price = request.GET.get('min_price', None)
    if min_price:
        tutors = tutors.filter(hourly_rate__gte=min_price)

    max_price = request.GET.get('max_price', None)
    if max_price:
        tutors = tutors.filter(hourly_rate__lte=max_price)

    #ratings = request.GET.get('ratings', None)
    #if ratings:
    #    tutors = tutors.filter(rating__gte=ratings)

    # Pagination
    tutors = tutors.order_by('user__username')  # or any order you prefer
    paginator = Paginator(tutors, 10)  # 10 tutors per page
    page_number = request.GET.get('page')
    tutors_page = paginator.get_page(page_number)

    context = {
        'form': TutorSearchForm(request.GET),  # Include the search form with current query params
        'tutors': tutors_page,
    }

    return render(request, 'tutor_search.html', context)