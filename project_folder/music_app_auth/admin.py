from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from.forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, AppLogging, OneTimeToken

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


class AppLoggingAdmin(admin.ModelAdmin):
    '''
    Custom admin configuration for the AppLogging model.
    This class controls how the logging entries are displayed and edited in the Django admin.
    '''
    list_display = ('user', 'timestamp', 'log_text')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__email', 'log_text')
    ordering = ('-timestamp',)
    

class OneTimeTokenAdmin(admin.ModelAdmin):
    '''
    Custom admin configuration for the OneTimeToken model.
    This class controls how the one time tokens are displayed and edited in the Django admin.
    '''
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('user', 'created_at', 'expires_at', 'is_used')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)


#Register admin models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AppLogging, AppLoggingAdmin)
admin.site.register(OneTimeToken, OneTimeTokenAdmin)


