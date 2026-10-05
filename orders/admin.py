from django.contrib import admin

from .models import ContactMessage, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'location', 'phone', 'delivery_date', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'product', 'delivery_date')
    search_fields = ('user__username', 'user__email', 'location', 'delivery_address', 'phone')
    date_hierarchy = 'created_at'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_read', 'created_at')
    list_editable = ('is_read',)
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)


admin.site.site_header = 'Joe Refill Admin'
admin.site.site_title = 'Joe Refill Admin'
admin.site.index_title = 'Orders & messages'
