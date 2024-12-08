from django.contrib import admin
from .models import CustomUser  # Import only CustomUser
from .models import TutorProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active', 'is_staff']
    list_filter = ['user_type', 'is_active']
    search_fields = ['username', 'email']

class TutorProfileAdmin(admin.ModelAdmin):
    # Display relevant tutor profile info
    list_display = ('user', 'location', 'hourly_rate', 'is_featured', 'profile_picture')

    # Make the 'is_featured' field editable directly from the list view
    list_editable = ('is_featured',)

    # Filter options for admin interface
    list_filter = ('is_featured', 'location')

    # Search fields for quick lookup in admin
    search_fields = ('user__username', 'location')

    # Admin form configuration
    fieldsets = (
        (None, {
            'fields': ('user', 'location', 'hourly_rate', 'is_featured', 'profile_picture', 'about_me', 'subjects', 'qualifications', 'availability')
        }),
    )

# Register the TutorProfile model with the custom admin class
admin.site.register(TutorProfile, TutorProfileAdmin)

