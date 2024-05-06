from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from order.models import Order, OrderProduct
from shop.models import Bookvariant
from userapp.models import WalletBook


@login_required(login_url='login')
def cancel_order(request, id):
    order_product = OrderProduct.objects.get(id=id)
    order_obj = Order.objects.get(id=order_product.order_id.id)
    order = order_product.order_id
    user=request.user
    print(order)
    try:
        payment = order.payment

        if request.method == 'POST':
            reason = request.POST['cancelReason']
            if reason:
                order_product.return_reason = reason
            order.status = "Cancelled"

            payment.status = 'Order cancelled'

            order_prod_obj=OrderProduct.objects.filter(order_id=order_obj)
            for i in order_prod_obj:
                book_variant = Bookvariant.objects.get(id=i.product.id)
                print("Before stock update:", book_variant.stock)
                i.item_cancel = True
                i.return_reason = reason
                book_variant.stock += i.quantity
                print("After stock update:", book_variant.stock)
                i.save()
                book_variant.save()


            if payment.payment_method!='Cash on delivery':
                amount=order.order_total
                refund_amount=float(amount)
                user.wallet=float(user.wallet)+float(refund_amount)
                user.save()

                wallet = WalletBook()
                wallet.customer = request.user
                wallet.description = "Cashback received due to the cancel of item"
                wallet.increment = True
                wallet.amount = f'{refund_amount}'
                wallet.save()



            order.save()
            payment.save()
        return redirect('ordersummary', id=order_obj.id)
    except Exception as e:
        print(e)
    return redirect('ordersummary', id=order_obj.id)

@login_required(login_url='login')
def orders_page(request):
    user = request.user
    orders = Order.objects.filter(user=user)


    context = {
        'orders': orders
    }
    return render(request,'userview/orders.html',context)


@login_required(login_url='login')
def order_summary(request,id):
    context={}
    try:
        if not 'email' in request.session:
            messages.error(request, 'You need to login for add to cart!')
            return redirect('userlogin')
        user = request.user
        order_obj=Order.objects.get(id=id)
        orders = OrderProduct.objects.filter(Q(user=user) and Q(order_id=order_obj))
        context={
            'orders':orders
        }
        return render(request, 'userview/ordersummary.html', context)
    except Exception as e:
        print(e)
    return render(request,'userview/ordersummary.html',context)


def order_return_item(request, id):
    order_item = OrderProduct.objects.get(id=id)
    try:
        if request.method == 'POST':
            return_reason = request.POST.get('returnReason', None)
            if return_reason:
                order_item.return_reason = return_reason
            order_item.return_request = True
        order_item.save()
        return redirect('ordersummary',id=order_item.order_id.id)
    except Exception as e:
        print(e)

    return redirect('order_view')


def return_request(request, id):
    try:

        order_item = OrderProduct.objects.get(id=id)
        variant = order_item.product
        order = order_item.order_id
        order_id = order.id

        user = order.user
        shipping = 0
        deduct_discount = 0
        tax = 0
        coupon = 0
        count = OrderProduct.objects.filter(order_id=order).count()

        if order.shipping > 0:
            if count < order.shipping:
                shipping = order.shipping / count

        if order.coupon_mount:
            if count < order.coupon_mount:
                coupon = order.coupon_mount / count

        if order.tax:
            if count < order.tax:
                tax = order.tax / count
        if request.method == 'POST':
            order_item.is_returned = True
            variant.stock += order_item.quantity
            amount = int(variant.discounted_price()) * order_item.quantity
            if coupon > 0:
                amount = amount - coupon
            if tax > 0:
                amount = amount + tax

            refund_amount = (float(amount) + float(shipping))  # calculating refund amount.

            user.wallet = float(user.wallet) + float(refund_amount)
            wallet_acc = WalletBook()
            wallet_acc.customer = user
            wallet_acc.amount = refund_amount
            wallet_acc.description = "Refund Credited for Product Return"
            wallet_acc.increment = True
            wallet_acc.save()
            order_item.save()
            variant.save()
            user.save()
            order.save()
            send_refund_email(user.email,refund_amount)
            return redirect('adminorderupdate', order_id)
    except Exception as e:
        print(e)
        return redirect('adminorder')



def send_refund_email(email, amount):
    try:
        subject = 'Return Successful'
        message = f'Your return request is accepted.Amount Rs.{amount} is credited to your wallet.Please Check your wallet!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(e)
    # Create your views here.
