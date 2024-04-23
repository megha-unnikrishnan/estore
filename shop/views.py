from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from shop.models import Wishlist, Bookvariant
from userapp.models import CustomUser


def add_to_wishlist(request, id):
    try:
        if not 'email' in request.session:
            messages.error(request, 'You need to login to add items to wishlist.')
            return redirect('login')

        product = Bookvariant.objects.get(id=id)
        user = request.user
        product_list = Wishlist.objects.filter(user=user, product=product)

        if product_list.exists():
            messages.info(request, f'"{product.variant_name}" is already in the wishlist!')
        else:
            wishlist_item = Wishlist.objects.create(user=user, product=product)
            wishlist_item.save()
            messages.success(request, f"'{product.variant_name}' added to wishlist successfully!")
            wishlist_count = Wishlist.objects.filter(user=user).count()
            request.session['wishlist'] = wishlist_count
            return redirect('productdetail', id=id)

    except Bookvariant.DoesNotExist:
        messages.error(request, 'Product does not exist.')
    except Exception as e:
        messages.warning(request, f'Oops! Something went wrong: {e}')

    return redirect('userindex')


def wishlistview(request):
    context = {}
    try:
        if not 'email' in request.session:
            messages.error(request, 'You need to login for add to wishlist!')
            return redirect('login')
        else:
            user=request.user
            wishlist = Wishlist.objects.filter(user=user)
            print(wishlist)

            context = {
                'items': wishlist,


            }

    except Exception as e:
        print(e)
    return render(request,'products/wishlist.html',context)


def wishlist_remove(request, id):
    try:
        if 'email' not in request.session:
            messages.error(request, 'You need to login to remove items from the wishlist!')
            return redirect('login')  # Redirect to login page
        else:
            product = Bookvariant.objects.get(id=id)
            wishlist_item = Wishlist.objects.filter(product=product, user=request.user).first()
            if wishlist_item:
                wishlist_item.delete()
                messages.success(request, f'{product.variant_name} removed from the wishlist')
            else:
                messages.warning(request, f"{product.variant_name} is not present in the wishlist")

        # Redirect to the referring URL or home


    except Bookvariant.DoesNotExist:
        messages.warning(request, 'Product does not exist')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('userindex')  # Redirect to home page if an error occurs
# Create your views here.
