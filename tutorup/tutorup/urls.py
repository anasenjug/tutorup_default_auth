
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/student/', views.student_register, name='register_student'),
    path('register/tutor/', views.tutor_register, name='register_tutor'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('tutor/profile/<int:pk>/', views.tutor_profile_view, name='tutor_profile_view'),
     path('tutor/profile/', views.tutor_profile_edit, name='tutor_profile_edit'),
]
