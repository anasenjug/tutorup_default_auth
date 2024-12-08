from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

def tutor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'tutor':
            return view_func(request, *args, **kwargs)
        return redirect(f"{reverse('login')}?next={request.path}")
    return _wrapped_view

def student_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'student':
            return view_func(request, *args, **kwargs)
        return redirect(f"{reverse('login')}?next={request.path}")
    return _wrapped_view

