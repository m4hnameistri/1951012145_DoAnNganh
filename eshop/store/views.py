from django.shortcuts import get_object_or_404,render
from .models import Category, Product
# Create your views here.


def product_all(request):
    products = Product.products.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug = slug, in_stock = True)
    return render(request, 'products/detail.html', {'product': product})

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug = category_slug)
    products = Product.products.filter(category = category)
    return render(request, 'products/category.html', {'category': category, 'products': products})