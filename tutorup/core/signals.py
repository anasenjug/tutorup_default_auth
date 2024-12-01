from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TutorProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_tutor_profile(sender, instance, created, **kwargs):
    if instance.user_type == 'tutor':
        if created:
            TutorProfile.objects.create(user=instance)
        else:
            # Save the profile if it already exists
            if hasattr(instance, 'tutor_profile'):
                instance.tutor_profile.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_tutor_profile(sender, instance, created, **kwargs):
    if instance.user_type == 'tutor':
        if created or not hasattr(instance, 'tutor_profile'):
            TutorProfile.objects.get_or_create(user=instance)
        else:
            instance.tutor_profile.save()
