from django.contrib import admin
from store.models import Order, Customer


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'membership', 'is_active']
    list_editable = ('membership',)
    list_per_page = 10
    list_filter = ('user__is_active',)
    list_select_related = ['user']
    search_fields = ['first_name__istartswith', 'user__last_name__istartswith']
    ordering = ('user__first_name', 'user__last_name')

    @admin.display(ordering='user__first_name',)
    def first_name(self, customer):
        return customer.user.first_name

    @admin.display(ordering='user__last_name',)
    def last_name(self, customer):
        return customer.user.last_name

    @admin.display(ordering='user__email',)
    def email(self, customer):
        return customer.user.email

    @admin.display(ordering='user__is_active',)
    def is_active(self, customer):
        return customer.user.is_active


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order', 'customer', 'payment_status',]


