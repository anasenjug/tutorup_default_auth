from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from .utils import *
from django.contrib.auth import logout, get_user_model
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView
from django.db import transaction
import sys

class CustomLoginView(LoginView):
    template_name = 'login.html'
    next_page = 'index'

    def form_invalid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user is not None and not user.is_active:
            if getattr(user, 'user_type', None) == 'tutor':
                return redirect('tutor_pending')
                
        return super().form_invalid(form)

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"You've succesfully registered! You can proceed to Login now.")
            return redirect('login')
        return render(request, {'form': form}, status=400)

    # Render form as a partial for htmx
    form = StudentRegistrationForm()
    return render(request, 'register_student.html', {'form': form})


def tutor_pending_view(request):
    """Simple view to render the approval landing page."""
    return render(request, 'tutor_pending.html')


def tutor_register(request):
    if request.method == 'POST':
        user_form = TutorRegistrationForm(request.POST)
        profile_form = TutorProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()
                    profile, created = TutorProfile.objects.get_or_create(user=user)
                    profile_form = TutorProfileForm(request.POST, request.FILES, instance=profile) 
                    profile_form.save()
                return redirect('tutor_pending')
            except Exception as e:
                # If something crashes at the database layer, show it in the terminal
                print(f"--- DATABASE ERROR: {e} ---", file=sys.stderr)
                user_form.add_error(None, "An unexpected database error occurred.")
        else:
            # CRITICAL DIAGNOSTIC: If forms are invalid, this prints the exact cause to your terminal
            print("--- USER FORM ERRORS ---", user_form.errors, file=sys.stderr)
            print("--- PROFILE FORM ERRORS ---", profile_form.errors, file=sys.stderr)
    else:
        user_form = TutorRegistrationForm()
        profile_form = TutorProfileForm()

    return render(request, 'register_tutor.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def index(request):
    featured_tutors = TutorProfile.objects.filter(is_featured=True)
    return render(request,'index.html',{'featured_tutors':featured_tutors})

def api_featured_tutors(request):
    featured_tutors = TutorProfile.objects.filter(is_featured=True)
    tutors_data = [
        {
            'id': tutor.id,
            'first_name': tutor.first_name,
            'last_name': tutor.last_name,
            'profile_picture': tutor.profile_picture.url if tutor.profile_picture else '',
            'rating': round(tutor.average_rating, 1) if tutor.average_rating else 'N/A',
            'review_count': tutor.review_count,
            'hourly_rate': tutor.hourly_rate,
            'location': tutor.location,
            'profile_url': reverse('tutor_profile_view', args=[tutor.user.id]),  # Add profile URL
        }
        for tutor in featured_tutors
    ]
    return JsonResponse(tutors_data, safe=False)

def about_us(request):
    return render(request, 'about_us.html')

@tutor_required
@login_required
def tutor_profile_edit(request):
    if request.user.user_type != 'tutor':
        return redirect('index')

    # Fetch the profile linked to this user securely
    profile, created = TutorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TutorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # FIXED: Redirect using the Profile's actual ID, NOT the User's account ID
            return redirect('tutor_profile_view', pk=request.user.pk)
    else:
        form = TutorProfileForm(instance=profile)

    return render(request, 'tutor_profile_edit.html', {'form': form})

@login_required
def tutor_profile_view(request, pk):
    # Pull profile along with user data in one clean DB hit
    tutor_profile = get_object_or_404(TutorProfile.objects.select_related('user'), user__pk=pk)

    if getattr(tutor_profile.user, 'user_type', None) != 'tutor':
        raise Http404("This profile does not belong to a valid tutor.")

    reviews = tutor_profile.reviews.all()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.tutor = tutor_profile  
            review.save()
            return redirect('tutor_profile_view', pk=pk)
    else:
        form = ReviewForm()
    
    context = {
        'tutor_profile': tutor_profile,
        'reviews': reviews,
        'form': form
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
    tutors = TutorProfile.objects.select_related('user').prefetch_related('reviews')

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
    paginator = Paginator(tutors, 3)  # 3 tutors per page
    page_number = request.GET.get('page')
    tutors_page = paginator.get_page(page_number)

    #Extract and preserve query parameters for the template pagination button
    get_copy = request.GET.copy()
    if 'page' in get_copy:
        del get_copy['page']
    query_params = get_copy.urlencode()


    context = {
        'form': TutorSearchForm(request.GET),  # Include the search form with current query params
        'tutors': tutors_page,
        'query_params': query_params,
    }

    if request.htmx:
        # If HTMX request, only return the search results part
        return render(request, 'partials/tutor_search_results.html', context)
    else:
        # Otherwise, render the full page
        context['form'] = TutorSearchForm(request.GET)
        return render(request, 'tutor_search.html', context)
    

def contact_us(request):
    sent = False
    form = ContactForm()

    if request.method == "POST":
        
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # collect and clean data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            email_body = (
                f"New message from your website contact form:\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Subject: {subject}\n\n"
                f"Message:\n{message}"
            )

            send_mail(
                subject=f"📩 Message from: {name}",
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
            )

            sent = True
            form = ContactForm()  # reset form upon success
        
        # return the htmx partial 
        if request.htmx:
            return render(request, "partials/contact_form.html", {
                "form": form,
                "sent": sent
            })

    return render(request, "contact_us.html", {
        "form": form,
        "sent": sent
    })

@login_required
def create_booking_request(request, tutor_user_id):
    tutor_profile = get_object_or_404(TutorProfile, user__pk=tutor_user_id)
    
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.tutor_profile = tutor_profile
            booking.rate_at_booking = tutor_profile.hourly_rate  
            booking.status = 'pending'
            booking.save()
            
            messages.success(request, "Your booking request has been sent successfully!")
            
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Trigger'] = 'bookingSuccess' # Signal sent to front-end
                return response
                
            return redirect('dashboard')
    
    return redirect('tutor_profile_view', pk=tutor_user_id)


@login_required
def respond_to_booking(request, booking_id):
    # Ensure the logged-in user actually owns the tutor profile receiving this request
    booking = get_object_or_404(BookingRequest, id=booking_id, tutor_profile__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action') # 'approve' or 'reject'
        
        if action == 'approve':
            booking.status = 'approved'
            booking.save()
            messages.success(request, "You have accepted this booking request!")
            
        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '').strip()
            if not reason:
                messages.error(request, "Please provide a brief reason for declining.")
                # CHANGED: Redirects to the central dashboard router
                return redirect('dashboard')
                
            booking.status = 'rejected'
            booking.rejection_reason = reason
            booking.save()
            messages.success(request, "Request declined and feedback sent to student.")
            
    return redirect('dashboard')

@login_required
def dashboard_router(request):
    # Route 1: User is a Tutor
    if getattr(request.user, 'user_type', None) == 'tutor':
        # Fetch all pending and history items for this specific tutor profile
        incoming_bookings = BookingRequest.objects.filter(tutor_profile__user=request.user)
        context = {
            'pending_bookings': incoming_bookings.filter(status='pending'),
            'booking_history': incoming_bookings.exclude(status='pending'),
        }
        return render(request, 'tutor_dashboard.html', context)
    
    # Route 2: User is a Student (Default Fallback)
    else:
        # Fetch all requests this student has sent out
        sent_bookings = BookingRequest.objects.filter(student=request.user)
        context = {
            'sent_bookings': sent_bookings
        }
        return render(request, 'student_dashboard.html', context)

@login_required
def cancel_booking_request(request, booking_id):
    # Ensure the request belongs to the logged-in student and is still pending
    booking = get_object_or_404(BookingRequest, id=booking_id, student=request.user)
    
    if booking.status == 'pending':
        booking.delete()
        messages.success(request, "Booking request cancelled successfully.")
    else:
        messages.error(request, "This booking cannot be cancelled because its status has changed.")

    # If using HTMX, return an empty body with a 200 OK so HTMX swaps nothing (removes row)
    if request.headers.get('HX-Request'):
        response = HttpResponse("")
        # Optional: trigger a full reload to show messages, or rely on HTMX swapping
        response['HX-Redirect'] = '/dashboard/' 
        return response

    return redirect('dashboard')