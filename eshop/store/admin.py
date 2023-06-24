from django.contrib import admin
from .models import Category, Product, User, Order, OrderItem
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','created','total_paid','billing_status')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order','product','price', 'quantity')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'in_stock', 'is_active')
    list_editable = ('is_active',)

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(User)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)