from .models import Category, Order, OrderItem
from django.db.models import Sum, Count

def all_categories(request):
    categories = Category.objects.all()
    return {'categories': categories} 

def top_10_products(request):
    top_8_products = OrderItem.objects.values('product').annotate(sum_quantity = Sum('quantity')).order_by('sum_quantity')[:8]
    return {'top_8_products': top_8_products }