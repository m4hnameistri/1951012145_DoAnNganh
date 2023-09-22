from django.contrib import admin
from django.urls.resolvers import URLResolver
from .models import Category, Product, User, Order, OrderItem
from django.urls import path
from datetime import datetime
from django.template.response import TemplateResponse
from .views import number_order_by_month, revenue_by_month, number_order_by_day, revenue_by_day


# Register your models here.
class CustomAdminSite(admin.AdminSite):
    site_header = 'Web bán hàng mỹ phẩm'
    site_title = 'Something'

    def get_urls(self) -> list[URLResolver]:
        return [
            path("chart/", self.stats_view)
        ] + super().get_urls()
    
    def stats_view(self, request):
        month = request.GET.get('month', datetime.now().month)
        year = request.GET.get('year', datetime.now().year)
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        orders = Order.objects.filter(billing_status = True)
        count_by_month = number_order_by_month(orders=orders,month=month, year=year, from_date=from_date, to_date=to_date)
        revenue_by_month_data = revenue_by_month(orders=orders ,month=month, year=year, from_date=from_date, to_date=to_date)
        count_by_day = number_order_by_day(orders=orders ,month=month, year=year, from_date=from_date, to_date=to_date)
        revenue_by_day_data = revenue_by_day(orders=orders ,month=month, year=year, from_date=from_date, to_date=to_date)
        # Order.objects.filter(id=61).update(created=datetime.strptime('07/09/2023', '%d/%m/%Y'))
        return TemplateResponse(request, "account/chart-stats.html", 
                                {'count_by_month': count_by_month, 'revenue_by_month': revenue_by_month_data, 
                                    'count_by_day': count_by_day, 'revenue_by_day': revenue_by_day_data})
    
custom_admin_site = CustomAdminSite('myweb')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','created','total_paid','billing_status')
    list_editable = ('billing_status',)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id','order','product','price', 'quantity')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'in_stock', 'is_active')
    list_editable = ('is_active',)


custom_admin_site.register(Category)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(User)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
