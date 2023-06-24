from django.shortcuts import render
import stripe
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from cart.cart import Cart
from store.models import Order, OrderItem
from importlib_metadata import metadata

# Create your views here.
@login_required
def CartView(request):
    cart = Cart(request)
    total = str(cart.total_cart_price())
    total = total.replace('.','')
    total = int(total)
    # total đang là decimal, muốn gửi 1 stipre intent thì dữ liệu phải là an integer
    stripe.api_key = 'sk_test_51LuBRaLihTrAeE0zvCJNShMUy7uFjUswg28bIodnnCKXwt8XLrQ9j42lQaCt1B8FI6g0IyJCIu5py3YHohyHbodl00HzuzFzxo'
    intent = stripe.PaymentIntent.create(
        amount= 10000, 
        currency= 'gbp',
        metadata= {'userid': request.user.id}
    )
    # intent sẽ trả về 1 client secret (unique cho mỗi transaction), ta sẽ dùng client secret để match với order 
    # để ta chuẩn bị lưu vào database
    
    return render(request, 'payment/form.html', {'client_secret': intent.client_secret}) 

def add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        user_id = request.user.id
        order_key = request.POST.get('order_key')
        cart_total = cart.total_cart_price()
        full_name = request.POST.get('full_name')
        add1 = request.POST.get('add1')
        add2 = request.POST.get('add2')
        phone = request.POST.get('phone')
        print(request.POST)
        if Order.objects.filter(order_key = order_key).exists():
            pass
        else:
            order = Order.objects.create(user_id = user_id, full_name = full_name, address1 = add1, phone = phone,
                                            address2 = add2, total_paid = cart_total, order_key = order_key)
            order_id = order.pk
            for item in cart:
                OrderItem.objects.create(order_id = order_id, product = item['product'], price = item['price'], quantity = item['soluong'])           
        return JsonResponse({'success': 'Ban da dat hang thanh cong!'})

def payment_confirmation(data):
    Order.objects.filter(order_key=data).update(billing_status=True)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None
    try:
        # hook into the stripe events
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)

    # Handle the event
    # When the client goes to the page to pay, we send a message to stripe and make the payment intent,
    # then the client secret gets returned from that so that's what we're going to look for because remember 
    # in our database we stored that in our database
    ### So we're going to do here is looking for in our database that clientsecret and if we find the order with that
    ### client secret we know that we've made the payment and we're going to update that order as completed (billing_status)
    if event.type == 'payment_intent.succeeded':
        payment_confirmation(event.data.object.client_secret)

    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)

def order_placed(request):
    cart = Cart(request)
    cart.clear()
    return render(request, 'payment/order_placed.html')
    