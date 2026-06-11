from django.contrib.auth import views as auth_views
from django.urls import path
from core import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Home page
    path('', views.index, name='index'),

    # Authentication
    path('accounts/login/', views.CustomLoginView.as_view(),name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('tutor/pending/', views.tutor_pending_view,name='tutor_pending'),

    # Registration
    path('register/student/', views.student_register, name='register_student'),
    path('register/tutor/', views.tutor_register, name='register_tutor'),

    # Tutor profile
    path('tutor/profile/<int:pk>/', views.tutor_profile_view, name='tutor_profile_view'),
    path('tutor/profile/edit/', views.tutor_profile_edit, name='tutor_profile_edit'),
    path('tutor/book/<int:tutor_user_id>/', views.create_booking_request, name='create_booking_request'),

    path('booking/respond/<int:booking_id>/', views.respond_to_booking, name='respond_to_booking'),

    path('booking/cancel/<int:booking_id>/', views.cancel_booking_request, name='cancel_booking_request'),

    path('api/featured-tutors', views.api_featured_tutors, name='api_featured_tutors'),
    # Search
    path('search/', views.tutor_search, name='tutor_search'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    path('about/',views.about_us, name='about_us'),
    path('contact/',views.contact_us,name='contact_us'),

    path('dashboard/', views.dashboard_router, name='dashboard')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
