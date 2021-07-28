from django.contrib import admin

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import *

# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username','email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        # ( 'Section Heading' , {'fields': ('fld1',) } ),
        ( 'Basic Information', {'fields': ('username','email', 'password')} ),
        ( 'Permissions', {'fields': ('is_admin','is_staff','is_active','is_superuser')} ),
        ( 'Details' , {'fields': ('first_name','last_name', 'dob', 'gender', 'blood_group','user_type',) } ),
        ( 'Address' , {'fields': ('address','city', 'district', ) } ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            #'fields': ('username', 'email', 'password1', 'password2'),
            'fields' : (
                'first_name',
                'last_name',
                'username',
                'email',
                'password1',
                'password2',
                'dob',
                'gender',
                'blood_group',
                'user_type',
            ),
        }),
    )
    search_fields = ('email','username','first_name','last_name','dob')
    ordering = ('email',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.


# Custom classes (by me)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__','apprived',)
    ordering = ('apprived',)

class DoctorAssistantProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__','doctor',)


########## REGISTERING other models ###############

admin.site.register(PatientProfile)
admin.site.register(DoctorProfile, DoctorProfileAdmin)
admin.site.register(DocAsstProfile, DoctorAssistantProfileAdmin)