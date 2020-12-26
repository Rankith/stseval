from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import User, Purchase


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password','stripe_customer')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'date_joined','last_login','is_staff','stripe_customer')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class PurchaseAdmin(ImportExportModelAdmin):
    list_display=('id','user','session','type','amount','quantity','stripe_payment')
    list_filter = ('session','type')

admin.site.register(Purchase,PurchaseAdmin)