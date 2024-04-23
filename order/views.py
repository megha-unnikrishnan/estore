from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from order.models import Order, OrderProduct
from shop.models import Bookvariant




@login_required(login_url='login')
def cancel_order(request, id):
    order_product = OrderProduct.objects.get(id=id)
    variant = Bookvariant.objects.get(id=order_product.product.id)
    order_obj = Order.objects.get(id=order_product.order_id.id)
    order = order_product.order_id
    print(order)
    try:
        payment = order.payment

        if request.method == 'POST':
            reason = request.POST['cancelReason']
            if reason:
                order_product.return_reason = reason
            order.status = "Cancelled"

            payment.status = 'Order cancelled'
            order_product.item_cancel = True
            variant.stock += order_product.quantity



            order.save()
            order_product.save()
            variant.save()
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
# Create your views here.
