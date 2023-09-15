from collections import Counter
import imp
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404,render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, DateField
from .tokens import activation_token
from .models import User, Order
from django.http import HttpResponse
from django.db.models import Q
from django.db.models.functions import Cast
from functools import reduce
import operator
from django.db.models.functions import TruncMonth,ExtractMonth, ExtractYear

from django.core.mail import EmailMessage
from django.core.paginator import Paginator

from .models import Category, Product
from .forms import (CreateUserForm, EditInfoForm)
# Create your views here.


def product_all(request):
    products = Product.products.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/home.html', {'products': products, 'page_obj': page_obj})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug = slug, in_stock = True)
    return render(request, 'products/detail.html', {'product': product})

def category_list(request, category_slug):
    category = get_object_or_404(Category, slug = category_slug)
    products = Product.products.filter(category = category)
    return render(request, 'products/category.html', {'category': category, 'products': products})

def search(request):
    q=request.GET['q']
    data=Product.objects.filter(Q(title__icontains = q) | Q(category__title__icontains = q)).order_by('-id')

    return render(request,'products/search.html',{'data':data})

# def user_register(request):
#     if request.user.is_authenticated:
#         return redirect('store:dashboard')

#     if request.method == 'POST':
#         # We don't want anyone can be able to register account if they don't
#         # actually post any data to us so this if will provide validation check.

#         form = CreateUserForm(request.POST)
#         # Create a form instance with POST data
#         if form.is_valid():
#             user = form.save(commit= False)
#             # This save() method accepts an optional commit keyword argument, which accepts either True or False. 
#             # If you call save() with commit=False, then it will return an object that hasn't yet been saved to the database.

#             user.email = form.cleaned_data['email']
#             # user.username = form.cleaned_data['user_name']
#             user.set_password(form.cleaned_data['password'])
#             user.is_active = False
#             # Set is_active = False vì cần 1 thủ tục kích hoạt via email để is_active = True
#             user.save()

#             #Setup email
#             current_site = get_current_site(request)
#             subject = 'Activate your account'
#             message = render_to_string('account/activate_account.html',
#             {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 # encoding a byte string into base64 string so we can use it in the url,
#                 'token': activation_token.make_token(user),
#             })
#             user.email_user(subject = subject, message = message)
#             return HttpResponse("Đăng kí thành công !!!")
#     else:
#         form = CreateUserForm()
#     return render(request, 'account/register.html', {'form': form})

def user_register(request):
    if request.user.is_authenticated:
        return redirect('store:dashboard')

    if request.method == 'POST':
        # We don't want anyone can be able to register account if they don't
        # actually post any data to us so this if will provide validation check.

        form = CreateUserForm(request.POST)
        # Create a form instance with POST data
        if form.is_valid():
            user = form.save(commit= False)
            # This save() method accepts an optional commit keyword argument, which accepts either True or False. 
            # If you call save() with commit=False, then it will return an object that hasn't yet been saved to the database.

            user.email = form.cleaned_data['email']
            # user.username = form.cleaned_data['user_name']
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            # Set is_active = False vì cần 1 thủ tục kích hoạt via email để is_active = True
            user.save()

            #Setup email
            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('account/activate_account.html',
            {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # encoding a byte string into base64 string so we can use it in the url,
                'token': activation_token.make_token(user),
            })
            # user.email_user(subject = subject, message = message)
            email = EmailMessage(subject = subject, body = message, to= [user.email])
            if email.send():
                return HttpResponse("Registration Successful !" f'Dear <b>{user}</b>, please go to you email <b>{user.email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.' )
            else:
                return HttpResponse(request, f'Problem sending email to {user.email}, check if you typed it correctly.')
    else:
        form = CreateUserForm()
    return render(request, 'account/register.html', {'form': form})


def user_activate(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    try:
        pass
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('store:dashboard')
    else:
        return render(request, 'account/fail_to_activate.html')

@login_required
def dashboard(request):
    orders = user_orders(request)
    return render(request, 'account/dashboard.html', {'orders' : orders})


# CHƯA LÀM
@login_required
def profile(request):
    return render(
            request,
            "account/profile.html",
            )

@login_required
def edit_info(request):
    if request.method == "POST":
        user_form = EditInfoForm(instance = request.user, data = request.POST)
        
        if user_form.is_valid():
            print(user_form)
            user_form.save()
    else:
        user_form = EditInfoForm(instance = request.user)
    return render(request, "account/edit_info.html", {'user_form': user_form})

def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return orders

def number_order_by_month(orders, month = None, from_date = None, to_date = None):
    if month:
        orders = orders.filter(created__month = month)
    if from_date:
        orders = orders.filter(created__gte = from_date)
    if to_date:
        orders = orders.filter(created__lt = to_date)
    # count_by_month = orders.raw("SELECT strftime('%m', created) as month, COUNT(*) as count, id FROM store_order WHERE billing_status = True GROUP BY strftime('%m', created)")
    count_by_month_data = orders.values('created__month').annotate(count=Count('id'))
    l = []
    for i in count_by_month_data:
        l.append({i['created__month']:i['count']})
    counter = Counter()
    for d in l:
        counter.update(d)

    result = dict(counter).items()
    return result

def number_order_by_day(orders, month = None, from_date = None, to_date = None):
    if month:
        orders = orders.filter(created__month = month)
    if from_date:
        orders = orders.filter(created__gte = from_date)
    if to_date:
        orders = orders.filter(created__lt = to_date)

    count_by_day_data = orders.values('created__day').annotate(count=Count('id'))
    l = []
    for i in count_by_day_data:
        l.append({i['created__day']:i['count']})
    counter = Counter()
    for d in l:
        counter.update(d)

    result = dict(counter).items()
    return result

def revenue_by_month(orders, month = None, from_date = None, to_date = None):
    if month:
        orders = orders.filter(created__month = month)
    if from_date:
        orders = orders.filter(created__gte = from_date)
    if to_date:
        orders = orders.filter(created__lt = to_date)
    # count_by_month = orders.raw("SELECT strftime('%m', created) as month, COUNT(*) as count, id FROM store_order WHERE billing_status = True GROUP BY strftime('%m', created)")
    revenue_by_month_data = orders.values('created__month').annotate(revenue=Sum('total_paid'))
    l = []
    for i in revenue_by_month_data:
        l.append({i['created__month']:i['revenue']})
    counter = Counter()
    for d in l:
        counter.update(d)
    result = dict(counter).items()
    return result

def revenue_by_day(orders, month = None, from_date = None, to_date = None):
    if month:
        orders = orders.filter(created__month = month)
    if from_date:
        orders = orders.filter(created__gte = from_date)
    if to_date:
        orders = orders.filter(created__lt = to_date)
    # count_by_month = orders.raw("SELECT strftime('%m', created) as month, COUNT(*) as count, id FROM store_order WHERE billing_status = True GROUP BY strftime('%m', created)")
    revenue_by_day_data = orders.values('created__day').annotate(revenue=Sum('total_paid'))
    l = []
    for i in revenue_by_day_data:
        l.append({i['created__day']:i['revenue']})
    counter = Counter()
    for d in l:
        counter.update(d)
    result = dict(counter).items()
    return result

def stats_view(request):
    
    # month = request.GET.get('month')
    # from_date = request.GET.get('from_date')
    # to_date = request.GET.get('to_date')
    # orders = Order.objects.filter(billing_status = True)
    
    # count_by_month = number_order_by_month(orders=orders, month=month, from_date=from_date, to_date=to_date)
    # revenue_by_month_data = revenue_by_month(orders=orders, month=month, from_date=from_date, to_date=to_date)
    # count_by_day = number_order_by_day(orders=orders, month=month, from_date=from_date, to_date=to_date)
    # return render(request, "account/chart-stats.html", 
    #               {'count_by_month': count_by_month, 'revenue_by_month': revenue_by_month_data, 'count_by_day': count_by_day})
    pass
