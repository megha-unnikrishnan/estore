from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.views import View

from order.models import Order, OrderProduct
from cart.models import CartItem
from .models import CustomUser, Forgotpassword, WalletBook
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import uuid
from userapp.helper import send_forget_password_mail
from shop.models import Category, Book, Bookvariant, MultipleImages, Author, Wishlist, ProductReview
from django import template
from django.views.decorators.cache import cache_control
from django.db.models import Q, Count, Max, Avg, Sum
from datetime import timedelta
from django.utils import timezone
from userapp.models import UserAddress
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from shop.models import Book
import razorpay
from decimal import Decimal
# module for print pdf
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
@cache_control(no_cache=True, no_store=True)
def index(request):
    context={}
    try:
        image = Bookvariant.objects.filter(is_active=True)

        variant = Bookvariant.objects.all()
        product = Book.objects.all()
        category = Category.objects.filter(is_active=True)
        user_id = request.user.id
        user_cart_items = CartItem.objects.filter(user_id=user_id)
        cart_item_count = user_cart_items.count()
        print('countindex',cart_item_count)
        request.session['cart']=cart_item_count
        user_wishlist_items = Wishlist.objects.filter(user_id=user_id)
        wishlist_item_count = user_wishlist_items.count()
        request.session['wishlist'] = wishlist_item_count
        # request.session.save()
        # print(request.session.save())
        context = {
            'image': image,
            'variant': variant,
            'category': category,
            'product': product,
            'cart':cart_item_count
        }

    except Exception as e:
        print(e)
    return render(request, 'userview/index.html', context)


def user_login(request):
    try:
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect('userindex')
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)

            if user and user.is_superuser == False:
                login(request, user)
                request.session['email']=email
                return redirect('userindex')
            else:
                messages.error(request, 'Invalid email or password')


    except Exception as e:
        print(e)

    return render(request, 'userview/login.html')
def generate_referral_code():
    code = str(uuid.uuid4()).replace('-', '')[:12]
    return code


def user_signup(request):
    try:
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect('userindex')
        if request.method == 'POST':
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            email = request.POST['email']
            phone = request.POST['mobile']
            password = request.POST['password']
            cpassword = request.POST['cpassword']
            referal=request.POST['referal']
            print(referal)
            if password == cpassword:
                if CustomUser.objects.filter(email=email).exists():
                    messages.info(request, 'Email already exists')
                    return redirect('register')
                elif CustomUser.objects.filter(phone=phone).exists():
                    messages.info(request, 'Mobile number already exists')
                    return redirect('register')
                else:
                    register = CustomUser.objects.create_user(first_name=firstname, last_name=lastname, email=email,
                                                              phone=phone, password=password)
                    print(register)
                    # generate otp
                    otp = get_random_string(length=6, allowed_chars='1234567890')
                    code = generate_referral_code()
                    register.otp = otp
                    register.referral_code = code

                    try:
                        if referal is not None:
                            ref_user = CustomUser.objects.filter(referral_code=referal).first()
                            print("refered user")
                            print(ref_user)


                            if ref_user:
                                referred_user = CustomUser.objects.get(id=ref_user.id)
                                referred_user.wallet += 200
                                register.wallet = 50
                                register.referred_by = referred_user.email
                                referred_user.save()
                                wallet_acc = WalletBook()
                                wallet_acc.customer = referred_user
                                wallet_acc.amount = referred_user.wallet
                                wallet_acc.description = "Referal  Amount Credited"
                                wallet_acc.increment = True
                                wallet_acc.save()
                                messages.success(request, "Referral code verified")
                            else:
                                messages.error(request, "Invalid Referral code.")
                    except Exception as e:
                        print(e)
                    register.save()
                    if register.wallet > 0:
                        wallet_acc = WalletBook()
                        wallet_acc.customer = register
                        wallet_acc.amount = register.wallet
                        wallet_acc.description = "Sign up bonus credited"
                        wallet_acc.increment = True
                        wallet_acc.save()
                        print(f"Sign up bonus of {register.wallet} credited to {register.email}")
                    otp_expiry_time = timezone.now() + timedelta(minutes=4)
                    register.otp_expiry_time = otp_expiry_time
                    send_otp_email(email, otp)
                    register.save()
                    return redirect('otp-verification', register.id)

            else:
                messages.info(request, 'password not matching')
                return redirect('register')


    except Exception as e:
        print(e)
    return render(request, 'userview/signup.html')


# def otp_verification(request, id):
#     try:
#         user = CustomUser.objects.get(id=id)
#         context = {'user': user}
#
#         if request.method == 'POST':
#             otp = request.POST.get('otp')
#
#             if len(otp) == 6 and otp == user.otp and user.otp_expiry_time > timezone.now():
#                 user.is_active = True
#                 user.otp = ''
#                 user.save()
#                 if user.wallet > 0:
#                     messages.success(request,
#                                      f"Account verified.You got a referal amount of Rs.{user.wallet} in your wallet.")
#                     return redirect('login')
#                 else:
#                     messages.success(request, "Account verified.")
#                     return redirect('login')
#
#             else:
#                 messages.error(request, "Invalid OTP or OTP expired. Please try again.")
#                 return redirect('otp-verification', id=user.id)
#
#
#     except Exception as e:
#         print(e)
#         messages.error(request, "Invalid OTP or OTP expired. Please try again.")
#     return render(request, 'userview/otp-verification.html', context)

def otp_verification(request, id):
    try:
        user = CustomUser.objects.get(id=id)
        context = {'user': user}

        if request.method == 'POST':
            otp = request.POST.get('otp')

            # Calculate OTP expiry time
            otp_expiry_time = user.otp_expiry_time

            if len(otp) == 6 and otp == user.otp and otp_expiry_time > timezone.now():
                user.is_active = True
                user.otp = ''
                user.save()
                if user.wallet > 0:
                    messages.success(request,
                                     f"Account verified. You got a referral amount of Rs.{user.wallet} in your wallet.")
                    return redirect('login')
                else:
                    messages.success(request, "Account verified.")
                    return redirect('login')

            else:
                messages.error(request, "Invalid OTP or OTP expired. Please try again.")
                return redirect('otp-verification', id=user.id)

        # Calculate OTP expiry time
        otp_expiry_time = user.otp_expiry_time

        # Add OTP expiry time to context
        context['otp_expiry_time'] = otp_expiry_time

    except Exception as e:
        print(e)
        messages.error(request, "Invalid OTP or OTP expired. Please try again.")
        return redirect('otp-verification', id=user.id)

    return render(request, 'userview/otp-verification.html', context)

def regenerate_otp(request, id):
    try:
        user = CustomUser.objects.get(id=id)
        email = user.email
        if user.last_otp_regeneration and (timezone.now() - user.last_otp_regeneration).total_seconds() < 60:
            messages.warning(request, "Please wait for 60 seconds before regenerating OTP.")
        else:
            otp = get_random_string(length=6, allowed_chars='1234567890')
            send_otp_email(email, otp)

            # Update user's OTP fields and last_otp_regeneration time
            user.otp = otp
            user.otp_expiry_time = timezone.now() + timedelta(minutes=1)
            user.last_otp_regeneration = timezone.now()
            user.save()

            messages.success(request, "New OTP sent to your email")
    except CustomUser.DoesNotExist:
        messages.error(request, "User does not exist")

    return redirect('otp-verification', user.id)


def send_otp_email(email, otp):
    subject = 'Your One-Time Password (OTP)'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

#
# def user_forgotpassword(request):
#     try:
#         if request.method == 'POST':
#             email = request.POST.get('email', None)
#             my_user = CustomUser.objects.get(email=email)
#             token = str(uuid.uuid4())
#             try:
#                 profile_token = Forgotpassword.objects.get(user=my_user.id)
#             except:
#                 profile_token = Forgotpassword.objects.create(user=my_user)
#             profile_token.forgot_password_token = token
#             profile_token.save()
#
#             send_forget_password_mail(email, token)
#
#             messages.success(request, "Password reset link sent to the email.")
#             return redirect('login')
#
#     except Exception as e:
#         messages.error(request, "User not found")
#         print(e)
#     return render(request, 'userview/forgotpassword.html')


def user_forgotpassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email', None)
            my_user = CustomUser.objects.get(email=email)

            # Check if the user is blocked
            if my_user.is_active:  # Assuming you have a field named is_active to track user's blocked status
                token = str(uuid.uuid4())
                try:
                    profile_token = Forgotpassword.objects.get(user=my_user.id)
                except:
                    profile_token = Forgotpassword.objects.create(user=my_user)
                profile_token.forgot_password_token = token
                profile_token.save()

                send_forget_password_mail(email, token)

                messages.success(request, "Password reset link sent to the email.")
                return redirect('login')
            else:
                messages.error(request, "User is blocked by admin")
                return redirect('login')  # or any other page you want to redirect to

    except CustomUser.DoesNotExist:
        messages.error(request, "User not found")
    except Exception as e:
        messages.error(request, "An error occurred")
        print(e)
    return render(request, 'userview/forgotpassword.html')

def change_password(request, token):
    context = {}

    profile = Forgotpassword.objects.filter(forgot_password_token=token).first()
    if profile is not None:
        if request.method == 'POST':
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')

            if password != cpassword:
                messages.error(request, "Password does not match.")
            else:
                user = profile.user
                user.set_password(password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('login')

        context = {
            'user_id': profile.user.id,
            'token': token,
        }
    else:
        messages.error(request, "Invalid or expired token. Please try again.")

    return render(request, 'userview/change-password.html', context)


@cache_control(no_cache=True, no_store=True)
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('userindex')


@cache_control(no_cache=True, no_store=True)
def product_detail(request, id):
    context = {}
    try:
        product = Bookvariant.objects.get(id=id)
        reviews = ProductReview.objects.filter(product=product)
        image = MultipleImages.objects.filter(product=product)
        related_products = Bookvariant.objects.filter(
            Q(author=product.author) | Q(edition=product.edition) | Q(category=product.category)
        )[:4]
        context = {
            'product': product,
            'image': image,
            'related_products': related_products,
            'reviews':reviews
        }

    except Exception as e:
        print(e)
    return render(request, 'userview/product-detail.html', context)




def search_view(request):
    if request.method == "GET":
        query = request.GET.get('query', '')
        suggestions = []
        if query:
            # Query your database for relevant suggestions based on the input query
            products = Book.objects.filter(product_name__icontains=query)[:5]
            if products:
                suggestions = [product.product_name for product in products]
            author = Author.objects.filter(author_name__icontains=query)[:5]
            if author:
                suggestions = [author.author_name for author in author]
            category = Category.objects.filter(category_name__icontains=query)[:5]
            if category:
                suggestions = [category.category_name for category in category]

        return JsonResponse({'suggestions': suggestions})
    elif request.method == "POST":
        query = request.POST.get('searchquery', '')
        search_result = Bookvariant.objects.filter(
            Q(product__product_name__icontains=query) |
            Q(author__author_name__icontains=query)| Q(category__category_name__icontains=query) ,
            product__is_active=True,
            is_active=True
        )
        context = {
            'listproducts': search_result,

            'query':query
        }
        return render(request, 'userview/search.html',context)


def sort_products(request):
    sort_order = request.GET.get('sort')

    if sort_order == 'low':
        products = Bookvariant.objects.filter(is_active=True).order_by('product_price')
    elif sort_order == 'high':
        products = Bookvariant.objects.filter(is_active=True).order_by('-product_price')
    elif sort_order=='newest':
        products = Bookvariant.objects.filter(is_active=True).order_by('-created_date')[:3]
    elif sort_order=='popular':

        top_products = OrderProduct.objects.filter(ordered=True, is_returned=False) \
                           .values('product') \
                           .annotate(total_quantity=Sum('quantity')) \
                           .order_by('-total_quantity')
        top_product_ids = [product['product'] for product in top_products]
        products = Bookvariant.objects.filter(id__in=top_product_ids)
    elif sort_order == 'rating':
        min_average_rating = 4
        products_with_avg_rating = Bookvariant.objects.annotate(avg_rating=Avg('rating'))
        products = products_with_avg_rating.filter(avg_rating__gte=min_average_rating)
    elif sort_order == 'stock':
        products = Bookvariant.objects.filter(stock__gt=0)
    elif sort_order =='outofstock':
        products = Bookvariant.objects.filter(stock=0)
    else:
        # Default sorting or handle invalid sorting parameter
        products = Bookvariant.objects.filter(is_active=True)
    paginator = Paginator(products, 4)  # Show 6 products per page
    page_number = request.GET.get('page')
    try:
        image_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        image_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        image_obj = paginator.page(paginator.num_pages)
    return render(request, 'userview/sortproducts.html', {'products':image_obj})

@cache_control(no_cache=True, no_store=True)
def product_list(request):
    image = Bookvariant.objects.filter(Q(is_active=True) and Q(product__is_active=True))
    category = Category.objects.all
    low = Bookvariant.objects.filter(is_active=True).order_by('product__product_price')
    high = Bookvariant.objects.filter(is_active=True).order_by('-product__product_price')
    paginator = Paginator(image, 4)
    try:
        page = int(request.GET.get('page', '1'))
        print(page)
    except:
        page = 1
    try:
        image_obj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        image_obj = paginator.page(paginator.num_pages)
    context = {
        'image': image_obj,
        'category': category,
        'low':low,
        'high':high
    }
    return render(request, 'userview/product-list.html', context)


@cache_control(no_cache=True, no_store=True)
def product_list_detail(request, id):
    context = {

    }

    try:
        product = Bookvariant.objects.get(id=id)
        image = MultipleImages.objects.filter(product=product)
        related_products = Bookvariant.objects.filter(
            Q(author=product.author) | Q(edition=product.edition) | Q(category=product.category)
        )
        paginator = Paginator(image, 10)  # Set 10 images per page
        page = request.GET.get('page')

        try:
            image_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            image_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            image_page = paginator.page(paginator.num_pages)
        print(image_page.number, image_page.paginator.num_pages, image_page.has_previous, image_page.has_next)
        context = {
            'product': product,
            'image': image,
            'related_products': related_products,
            'image_page':image_page

        }

    except Exception as e:
        print(e)
    return render(request, 'userview/product-list-detail.html', context)


def category_list(request, id):
    category = Category.objects.get(id=id)
    products = category.bookvariant_set.all()

    context = {
        'category': category,
        'products': products
    }
    return render(request, 'userview/category.html', context)


def category_detail(request, id):
    context = {}
    try:
        product = Bookvariant.objects.get(id=id)
        image = MultipleImages.objects.filter(product=product)
        related_products = Bookvariant.objects.filter(
            Q(author=product.author) | Q(edition=product.edition) | Q(category=product.category)
        )
        context = {
            'product': product,
            'image': image,
            'related_products': related_products
        }

    except Exception as e:
        print(e)
    return render(request, 'userview/category-detail.html', context)


def userprofile(request):
    try:
        if 'email' in request.session:


            return render(request, 'userview/userprofile.html')
        return redirect('userindex')
    except Exception as e:
        print(e)



@login_required
def addaddress(request, id):

        try:

            user=request.user
            if request.method == 'POST':
                name = request.POST['name']
                mobile = request.POST['mobile']
                address = request.POST['address']
                town = request.POST['town']
                zipcode = request.POST['zipcode']
                location = request.POST['location']
                district = request.POST['district']
                state = request.POST['state']

                # Create UserAddress object and associate it with the user
                address = UserAddress(
                    user=user,
                    name=name,
                    alt_mobile=mobile,
                    address=address,
                    town=town,
                    zipcode=zipcode,
                    nearby_location=location,
                    district=district,
                    state=state
                )
                address.save()

                if id == 1:
                    messages.success(request, "Address created")
                    return redirect('checkoutview',id=address.id)
                else:
                    messages.success(request, "New address added.")
                    return redirect('addressbook')

            return render(request, 'userview/addaddress.html')
        except CustomUser.DoesNotExist:
            # If the user with the provided id does not exist, handle the error
            messages.error(request, "User does not exist.")
            return redirect('addressbook')  # Redirect to a suitable page or handle as per your application's logic


def address_book(request):
    context={}
    try:
        if 'email' in request.session:
            user=request.user
            address=UserAddress.objects.filter(user=user)
            context={
                'address':address
            }

        return redirect('userlogin')
    except Exception as e:
        print(e)
    return render(request, 'userview/addressbook.html', context)



def deleteaddress(request,id):

    try:
        user = UserAddress.objects.get(id=id)
        user.delete()
        messages.success(request,'Delete successfully')
        return redirect('addressbook')
    except Exception as e:
        print(e)
        messages.error(request,'delete failed')
    return redirect(request,'userview/addressbook.html')


def updateaddress(request,id,o_id):
    if 'email' in request.session:
        context = {}
        try:
            address = UserAddress.objects.get(id=id)
            context = {'address': address,
                       'districts': ['Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kollam', 'Kottayam', 'Kozhikode', 'Malappuram', 'Palakkad', 'Pathanamthitta', 'Thiruvananthapuram', 'Thrissur', 'Wayanad']}
            if request.method == "POST":
                address.name = request.POST['name']
                address.address = request.POST['address']
                address.town = request.POST['town']
                address.zipcode = request.POST['zipcode']
                address.nearby_location = request.POST['location']
                address.district = request.POST['district']
                address.state = request.POST['state']
                address.save()
                if o_id== 0:
                    messages.success(request, "Succesfully saved")
                    return redirect('addressbook')
                else:
                    address = UserAddress.objects.get(id=id)
                    messages.success(request, "Succesfully saved")
                    return redirect('checkoutview',id=address.id)




        except Exception as e:
            print(e)
            messages.info(request, "Succesfully saved")
        return render(request, 'userview/update-address.html', context)
    return redirect('userindex')



def changeuserpassword(request):
    try:
        user = request.user
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.method == "POST":
                oldpassword = request.POST['oldpassword']
                newpassword = request.POST['newpassword']
                confirmpassword = request.POST['confirmpassword']

                if not user.check_password(oldpassword):
                    messages.error(request, 'Please enter the correct password!')
                    return redirect('changeuserpassword')

                if oldpassword == newpassword or oldpassword == confirmpassword:
                    messages.error(request, 'The new password is the same as your old password. Please change.')
                    return redirect('changeuserpassword')

                if newpassword != confirmpassword:
                    messages.error(request, "Password mismatch")
                    return redirect('changeuserpassword')


                user.set_password(newpassword)
                user.save()


                logout(request)

                messages.success(request, "Password changed successfully! Please log in again.")
                return redirect('login')
            return render(request, 'userview/change-user-password.html')
        else:
            messages.error(request, 'You need to login first')
            return redirect('userindex')
    except Exception as e:
        print(e)
        return render(request, 'userview/change-user-password.html')


def profiledetails(request):
    if 'email' in request.session:
        try:
            user = request.user

            if request.method == 'POST':
                # Get the updated values from the form submission
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')

                mobile = request.POST.get('mobile')

                # Update the user object with the new values
                user.first_name = first_name
                user.last_name = last_name

                user.phone = mobile
                user.save()  # Save the changes

                messages.success(request, 'User details updated successfully')
                return redirect('profiledetails')

            context = {'user': user}
            return render(request, 'userview/profiledetails.html', context)

        except Exception as e:
            print(e)
            messages.error(request, 'An error occurred while updating user details')
            return redirect('userindex')

    return redirect('userindex')


def updateprofile(request):
    if request.method == 'POST':
        # Get the updated values from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Update the user object with the new values
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.mobile = mobile
        user.save()  # Save the changes

        messages.success(request, 'User details updated successfully.')
        return redirect('profile_details')  # Redirect to the user profile page

    return render(request, 'userview/update_user_details.html')


def add_wallet(request):
    if 'email' in request.session:
        try:
            user = request.user
            data = WalletBook.objects.filter(customer=user)
            amount_paise = Decimal('0')
            if 'amount' in request.GET:
                amount = request.GET.get('amount')
                user.wallet += Decimal(amount)
                user.save()
                wallet_account = WalletBook()
                wallet_account.customer = user
                wallet_account.amount = amount
                wallet_account.description = "Added Money to wallet"
                wallet_account.increment = True
                wallet_account.save()
                messages.success(request, f"Amound Rs.{amount} added to the wallet!!")
                return redirect('add_wallet')

            context = {
                'user': user,
                'amount_paise': amount_paise,
                'data':data
            }
            return render(request, 'userview/wallet.html', context)
        except Exception as e:
            print(e)
    return redirect('userindex')



def wallet_book(request):
    user=request.user
    data=WalletBook.objects.filter(customer=user.id).order_by('-id')
    context={
        'data':data
    }
    return render(request,'userview/walletbook.html',context)


def write_review(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            if request.method == "POST":
                rating = request.POST.get('rating')
                review_desc = request.POST.get('review_desc')
                product_id = request.POST.get('id')
                title=request.POST.get('title')
                if product_id is None:
                    return HttpResponse("Product ID is missing in the form data.")

                try:
                    product = Bookvariant.objects.get(id=product_id)
                except Bookvariant.DoesNotExist:
                    messages.error(request, 'Product does not exist.')
                    return redirect('productdetail', id=product_id)

                user_id = CustomUser.objects.get(id=request.user.id)

                # Use filter() instead of get() to handle multiple OrderProduct objects
                order_products = OrderProduct.objects.filter(user=user_id, product=product, item_cancel=False,
                                                             return_request=False)

                if not order_products.exists():
                    messages.error(request, 'To provide a review for the product, you must first make a purchase of the item.')
                    return redirect('productdetail', id=product_id)

                try:
                    reviewcheck = ProductReview.objects.get(user=user_id, product=product)
                    messages.error(request, 'Review already exists!')
                    return redirect('productdetail', id=product_id)
                except ProductReview.DoesNotExist:
                    pass

                review = ProductReview(product=product, rating=rating, text=review_desc, user=user_id,title=title)
                review.save()
                messages.success(request, 'Review saved successfully!')
                return redirect('productdetail', id=product_id)
        except Exception as e:
            print(e)
            messages.error(request, 'An error occurred while processing your request.')
        return redirect('productdetail', id=product_id)
    else:
        return redirect('login')

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class viewinvoice(View):
    def get(self, request, order_id, *args, **kwargs):
        user = request.user
        try:
            id = OrderProduct.objects.get(id=order_id).order_id.id
            order = Order.objects.get(id=id)
            order_products = OrderProduct.objects.filter(order_id=order)
            data = {
                "company": "ESTORE",
                "address": "ERNAKULAM STREET",
                "city": "Ernakulam",
                "state": "Kerala",
                "zipcode": "678654",

                "phone": "+91 9008761234",
                "email": "estore@gmail.com",
                "website": "estore.com",
                "user": order.address.name,
                "customer_address": order.address.address,
                "town": order.address.town,
                "customer_email": user.email,
                "nearby_location": order.address.nearby_location,
                "district": order.address.district,
                "zip_code": order.address.zipcode,
                "customer_phone": user.phone,
                "order_products": order_products,
                "order": order,

            }

        except Exception as e:
            print(e)
            return HttpResponse(False)
        pdf = render_to_pdf('userview/order_invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class downloadinvoice(View):
    def get(self, request, order_id, *args, **kwargs):
        user = request.user
        try:
            id = OrderProduct.objects.get(id=order_id).order_id.id
            order = Order.objects.get(id=id)
            order_products = OrderProduct.objects.filter(order_id=order)
            data = {
                "company": "ESTORE",
                "address": "ERNAKULAM STREET",
                "city": "Ernakulam",
                "state": "Kerala",
                "zipcode": "678654",

                "phone": "+91 9008761234",
                "email": "estore@gmail.com",
                "website": "estore.com",
                "user": order.address.name,
                "customer_address": order.address.address,
                "town": order.address.town,
                "customer_email": user.email,
                "nearby_location": order.address.nearby_location,
                "district": order.address.district,
                "zip_code": order.address.zipcode,
                "customer_phone": user.phone,
                "order_products": order_products,
                "order": order,

            }


        except Exception as e:
            print(e)

        pdf = render_to_pdf('userview/order_invoice.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "orderinvoice_%s.pdf" % ("345678")
        content = "attachment; filename=%s" % (filename)  # Remove the quotes around filename
        response['Content-Disposition'] = content
        return response

def contacts(request):
    try:
        if request.method == 'GET':
            name = request.GET['name']
            email = request.GET['email']
            message = request.GET['message']
            head = 'meghamohan2006@gmail.com'

            subject = f"Queries from {name} "
            message = f'email {email}\n messaage : {message}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [head, ]
            send_mail(subject, message, email_from, recipient_list)

            messages.success(request, "Message sent successfully")
            return redirect('contacts')
    except Exception as e:
        print(e)
    return render(request,'userview/contacts.html')