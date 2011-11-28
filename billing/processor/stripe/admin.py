from django.contrib import admin

from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    search_fields = [
    	'billing_account__owner__id',
    	'billing_account__owner__username',
    	'billing_account__owner__email']
    raw_id_fields = ['billing_account']

admin.site.register(Customer, CustomerAdmin)
