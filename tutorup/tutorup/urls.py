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
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html',next_page='index'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Registration
    path('register/student/', views.student_register, name='register_student'),
    path('register/tutor/', views.tutor_register, name='register_tutor'),

    # Tutor profile
    path('tutor/profile/<int:pk>/', views.tutor_profile_view, name='tutor_profile_view'),
    path('tutor/profile/edit/', views.tutor_profile_edit, name='tutor_profile_edit'),
    path('api/featured-tutors', views.api_featured_tutors, name='api_featured_tutors'),
    # Search
    path('search/', views.tutor_search, name='tutor_search'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)