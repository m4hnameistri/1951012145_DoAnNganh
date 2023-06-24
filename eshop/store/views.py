import imp
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404,render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.decorators import login_required
from .tokens import activation_token
from .models import User, Order
from django.http import HttpResponse
from django.db.models import Q


from .models import Category, Product
from .forms import (CreateUserForm, EditInfoForm)
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

def search(request):
    q=request.GET['q']
    data=Product.objects.filter(Q(title__icontains = q) | Q(category__title__icontains = q)).order_by('-id')

    return render(request,'products/search.html',{'data':data})

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
            user.email_user(subject = subject, message = message)
            return HttpResponse("Đăng kí thành công !!!")
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