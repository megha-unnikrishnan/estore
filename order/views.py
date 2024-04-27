from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from order.models import Order, OrderProduct
from shop.models import Bookvariant
from userapp.models import WalletBook


@login_required(login_url='login')
def cancel_order(request, id):
    order_product = OrderProduct.objects.get(id=id)
    # variant = Bookvariant.objects.get(id=order_product.product.id)
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
# Create your views here.
