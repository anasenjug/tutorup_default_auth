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
        return render(request, {'form': form}, status=400)

    # Render form as a partial for htmx
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
    featured_tutors = TutorProfile.objects.filter(is_featured=True)
    return render(request,'index.html',{'featured_tutors':featured_tutors})

def api_featured_tutors(request):
    featured_tutors = TutorProfile.objects.filter(is_featured=True)
    tutors_data = [
        {
            'id': tutor.id,
            'first_name': tutor.user.first_name,
            'last_name': tutor.user.last_name,
            'profile_picture': tutor.profile_picture.url if tutor.profile_picture else '',
            'rating': getattr(tutor.user, 'profile', {}).get('rating', 'N/A'),
            'hourly_rate': tutor.hourly_rate,
            'location': tutor.location,
            'profile_url': reverse('tutor_profile_view', args=[tutor.user.id]),  # Add profile URL
        }
        for tutor in featured_tutors
    ]
    return JsonResponse(tutors_data, safe=False)

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

    reviews = tutor_profile.reviews.all()
    form = ReviewForm()
    if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.student = request.user
                review.tutor = tutor_profile
                review.save()
                return redirect('tutor_profile_view', pk=pk)
    
    context = {
        'tutor_profile': tutor_profile,
        'reviews' : reviews,
        'form' : form
    }

    return render(request, 'tutor_profile_view.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Ensure only the author can delete their review
    if request.user == review.student:
        review.delete()

    return redirect('tutor_profile_view', pk=review.tutor.user.pk)  # Redirect back to tutor profile

@login_required
@student_required
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

    if request.htmx:
        # If HTMX request, only return the search results part
        return render(request, 'partials/tutor_search_results.html', context)
    else:
        # Otherwise, render the full page
        context['form'] = TutorSearchForm(request.GET)
        return render(request, 'tutor_search.html', context)
    
