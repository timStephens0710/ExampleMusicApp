from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from.forms import RegistrationForm, CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(DefaultUserAdmin):
    '''
    Custom admin configuration for the CustomUser model.
    This class controls how the user is displayed and edited in the Django admin.
    '''
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    #Columns in the table
    list_display = ('email', 'username', 'is_active', 'date_joined', 'email_verified')

    #Fields to filter on
    list_filter = ('email', 'username', 'is_active', 'email_verified')

    #fieldsets variable controls how the 'change user' form looks on the Admin page, when we edit and existing user
    fieldsets = (
        (None, {'fields': ('email', 'username')}),       
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('email_verified',)}),    
        )


    #add_fieldsets variable controls how the 'add user' forms looks on the Admin page, when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_staff', 'is_superuser', 'is_active',
                'groups', 'user_permissions', 'email_verified'
            ),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)


