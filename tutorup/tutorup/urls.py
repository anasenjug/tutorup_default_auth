"""
URL configuration for tutorup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
      path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/student/', views.student_register, name='register_student'),
    path('register/user/', views.user_register, name='register_user'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
]
