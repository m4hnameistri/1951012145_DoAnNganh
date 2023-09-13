from django.contrib import admin
from django.urls.resolvers import URLResolver
from .models import Category, Product, User, Order, OrderItem
from django.urls import path
from .views import stats_view
from django.template.response import TemplateResponse
from .views import number_order_by_month, revenue_by_month


# Register your models here.
class CustomAdminSite(admin.AdminSite):
    site_header = 'Web bán hàng mỹ phẩm'
    site_title = 'Something'

    def get_urls(self) -> list[URLResolver]:
        return [
            path("chart/", self.stats_view)
        ] + super().get_urls()
    
    def stats_view(self, request):
        month = request.GET.get('month')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        count_by_month = number_order_by_month(month=month, from_date=from_date, to_date=to_date)
        revenue_by_month_data = revenue_by_month(month=month, from_date=from_date, to_date=to_date)
        return TemplateResponse(request, "account/chart-stats.html", {'count_by_month': count_by_month, 'revenue_by_month': revenue_by_month_data})
    
custom_admin_site = CustomAdminSite('myweb')

class MyModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("my_view/", self.admin_site.admin_view(self.my_view))]
        return my_urls + urls

    def my_view(self, request):
        # ...
        context = dict(
            # Include common variables for rendering the admin template.
            self.admin_site.each_context(request),
            # Anything else you want in the context...
            key=1,
        )
        return TemplateResponse(request, "account/chart-stats.html", context)
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','created','total_paid','billing_status')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order','product','price', 'quantity')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'in_stock', 'is_active')
    list_editable = ('is_active',)


custom_admin_site.register(Category)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(User)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
