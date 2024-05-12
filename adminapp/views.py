from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count, When, Case, Value, CharField
from django.db.models.functions import ExtractYear, ExtractMonth, Coalesce
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.datetime_safe import date
from django.views.decorators.cache import cache_control
import io
import base64
from order.models import Order, OrderProduct
from userapp.models import CustomUser
from shop.models import Category,Author,Book,Offer,Bookvariant,MultipleImages,Editions
import os
from cart.models import Coupons
from adminapp.forms import CategoryUpdateform
from datetime import datetime, timedelta
from django import template
import calendar
import matplotlib.pyplot as plt
register = template.Library()

@register.filter
def month_name(month_number):
    month_number = int(month_number)
    return calendar.month_name[month_number]

def admin_login(request):
    try:
        if request.user.is_superuser and request.user.is_authenticated:
            return redirect('admindashboard')
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    request.session['email'] = email
                    return redirect('admindashboard')
                else:
                    messages.info(request, "Invalid credentials")
            else:
                messages.info(request, "Invalid credentials")
                return redirect('adminlogin')

    except Exception as e:
        print(e)
        return redirect('adminlogin')
    return render(request, 'adminview/login.html')




def admin_dashboard(request):
    if 'email' in request.session:
        context={}
        try:
            orders = OrderProduct.objects.all().order_by('-id')
            order_count = orders.count()
            order_total = Order.objects.aggregate(total=Sum('order_total'))['total']
            today = date.today()
            today_count = Order.objects.filter(created__date=today).count()
            today_revenue = Order.objects.filter(created__date=today).aggregate(total=Sum('order_total'))['total']
            if request.method == 'POST':
                date_from = request.POST.get('startDate')
                date_to = request.POST.get('endDate')

                date_format = '%Y-%m-%d'
                try:
                    date_from = datetime.strptime(date_from, date_format)
                    date_to = datetime.strptime(date_to, date_format)

                    # Adjust end date to end of the day (23:59:59)
                    date_to += timedelta(days=1)  # Move to the next day
                    date_to -= timedelta(seconds=1)  # Go back one second to reach the end of the selected day

                except ValueError:
                    return HttpResponseBadRequest('Invalid date format')

                # Filter orders based on the selected date range
                orders = OrderProduct.objects.filter(order_id__created__range=(date_from, date_to))

            # Calculate yearly sales
            yearly_sales = (
                Order.objects
                .annotate(year=ExtractYear('created'))
                .values('year')
                .annotate(year_total=Sum('order_total'))
                .order_by('year')
            )


            # Calculate yearly orders
            yearly_orders = (
                Order.objects
                .annotate(year=ExtractYear('created'))
                .values('year')
                .annotate(total_orders=Count('id'))
                .order_by('year')
            )

            # Calculate monthly sales
            monthly_sales = (
                Order.objects
                .annotate(year=ExtractYear('created'), month=ExtractMonth('created'))
                .annotate(
                    month_name=Case(
                        When(month=1, then=Value('January')),
                        When(month=2, then=Value('February')),
                        When(month=3, then=Value('March')),
                        When(month=4, then=Value('April')),
                        When(month=5, then=Value('May')),
                        When(month=6, then=Value('June')),
                        When(month=7, then=Value('July')),
                        When(month=8, then=Value('August')),
                        When(month=9, then=Value('September')),
                        When(month=10, then=Value('October')),
                        When(month=11, then=Value('November')),
                        When(month=12, then=Value('December')),
                        output_field=CharField(),
                    )
                )
                .values('year', 'month_name')
                .annotate(monthly_total=Sum('order_total'))
                .order_by('year', 'month')
            )

            chart_labels = []
            chart_datas = []
            for sale in monthly_sales:
                chart_labels.append(sale['month_name'])
                chart_datas.append(sale['monthly_total'])




            # Calculate monthly orders
            monthly_orders = (
                Order.objects
                .annotate(year=ExtractYear('created'), month=ExtractMonth('created'))
                .annotate(
                    month_name=Case(
                        When(month=1, then=Value('January')),
                        When(month=2, then=Value('February')),
                        When(month=3, then=Value('March')),
                        When(month=4, then=Value('April')),
                        When(month=5, then=Value('May')),
                        When(month=6, then=Value('June')),
                        When(month=7, then=Value('July')),
                        When(month=8, then=Value('August')),
                        When(month=9, then=Value('September')),
                        When(month=10, then=Value('October')),
                        When(month=11, then=Value('November')),
                        When(month=12, then=Value('December')),
                        output_field=CharField(),
                    )
                )
                .values('year', 'month_name')
                .annotate(total_orders=Count('id'))
                .order_by('year', 'month')
            )
            #current weekly sales data
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            weekly_count = Order.objects.filter(created__date__range=[week_start, week_end]).count()
            weekly_revenue = Order.objects.filter(created__date__range=[week_start, week_end]).aggregate(total=Sum('order_total'))[
                'total']

            # current Monthly sales data
            month_start = today.replace(day=1)
            month_end = month_start.replace(month=month_start.month % 12 + 1) - timedelta(days=1)
            monthly_count = Order.objects.filter(created__date__range=[month_start, month_end]).count()
            monthly_revenue =Order.objects.filter(created__date__range=[month_start, month_end]).aggregate(total=Sum('order_total'))[
                'total']

            #current year sales



            # Get the start date of the current year
            year_start = datetime(datetime.now().year, 1, 1)

            # Get the end date of the current year
            year_end = datetime(datetime.now().year, 12, 31)

            # Filter orders for the current year
            current_yearly_count = Order.objects.filter(created__date__range=[year_start, year_end]).count()

            # Calculate the total revenue for the current year
            current_yearly_revenue = Order.objects.filter(created__date__range=[year_start, year_end]).aggregate(total=Sum('order_total'))[
                'total']

            # Calculate the total sum of discount_amount, coupon_amount, and category_amount
            total_discount = Order.objects.aggregate(
                total_discount=Sum('discount_amount') + Sum('coupon_mount') + Sum('category_amount')
            )['total_discount']

            # Now you have the total sum, you can assign it to a common variable
            common_discount = total_discount if total_discount else 0


            # product
            most_ordered_books = OrderProduct.objects.values('product__product__product_name').annotate(
                total_quantity=Coalesce(Sum('quantity'), 0)).order_by('-total_quantity')
            # Extract data for plotting
            book_names = [item['product__product__product_name'] for item in most_ordered_books]
            quantities = [item['total_quantity'] for item in most_ordered_books]


            # catgeory
            most_ordered_category_books = OrderProduct.objects.values('product__category__category_name').annotate(
                total_quantity=Coalesce(Sum('quantity'), 0)).order_by('-total_quantity')
            # Extract data for plotting
            category_book_names = [item['product__category__category_name'] for item in most_ordered_category_books]
            cat_quantities = [item['total_quantity'] for item in most_ordered_category_books]


            current_year_start = datetime(datetime.now().year, 1, 1)

            # Calculate year-wise order total
            yearly_order_totals = (
                Order.objects
                .filter(created__gte=current_year_start)
                .annotate(year=ExtractYear('created'))
                .values('year')
                .annotate(year_total=Sum('order_total'))
                .order_by('year')
            )
            start_year = 2021  # Change this to your start year
            current_year = datetime.now().year
            all_years = list(range(start_year, current_year + 1))

            # Retrieve the actual yearly sales data
            yearly_sales_data = {sale['year']: sale['year_total'] for sale in yearly_order_totals}

            # Populate the chart data
            chart_data = []
            for year in all_years:
                year_total = yearly_sales_data.get(year,
                                                   0)  # Get the total sales for the year, or set it to 0 if no data available
                chart_data.append(year_total)
            context={
                'order_count':order_count,
                'order_total':order_total,
                'today_count':today_count,
                'today_revenue':today_revenue,
                'orders':orders,
                'yearly_sales':yearly_sales,
                'yearly_orders':yearly_orders,
                'weekly_count': weekly_count,
                'weekly_revenue': weekly_revenue,
                'monthly_count': monthly_count,
                'monthly_revenue': monthly_revenue,
                'current_yearly_count':current_yearly_count,
                'current_yearly_revenue':current_yearly_revenue,
                'common_discount':common_discount,
                'monthly_sales':monthly_sales,
                'monthly_orders':monthly_orders,
                'most_ordered_books ':most_ordered_books,
                'book_names': book_names,
                'quantities': quantities,
                'yearly_order_totals':yearly_order_totals,
                'chart_data':chart_data,
                'all_years':all_years,
                'chart_labels':chart_labels,
                'chart_datas':chart_datas,
                'category_book_names':category_book_names,
                'cat_quantities':cat_quantities
            }
        except Exception as e:
            print(e)
        return render(request, 'adminview/admindashboard.html',context)
    return redirect('adminlogin')



def admin_logout(request):
    logout(request)
    return redirect('adminlogin')



def admin_users(request):
    try:
        if 'email' in request.session:
            user = CustomUser.objects.all()
            context = {'user': user}
            return render(request, 'adminview/admin-users.html', context)
        return redirect('adminlogin')
    except Exception as e:
        print(e)

def admin_action(request, id):
    user = CustomUser.objects.get(id=id)
    print(user)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('users')


@cache_control(no_cache=True, no_store=True)
def admin_category_action(request, id):
    user = Category.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('admincategory')

@cache_control(no_cache=True, no_store=True)
def admin_add_product(request):
    if 'email' in request.session:
        try:
            if request.method=='POST':
                name=request.POST['name']
                image = request.FILES.get('image')
                description = request.POST['description']
                review = request.POST['review']

                book=Book(product_name=name,product_image=image,product_desc=description,review=review)
                print(book)
                book.save()
                messages.success(request,"successfully saved")
                return redirect("adminproduct")

        except Exception as e:
            print(e)
            messages.error(request, "Save Failed")
            return redirect("adminproduct")
        return render(request, 'adminview/admin-add-product.html')
    return redirect('adminlogin')

@cache_control(no_cache=True, no_store=True)
def admin_author_action(request, id):
    user = Author.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('adminauthor')

@cache_control(no_cache=True, no_store=True)
def admin_product_action(request, id):
    user = Book.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('adminproduct')


@cache_control(no_cache=True, no_store=True)
def admin_edit_product(request,id):
    if 'email' in request.session:
        context = {}
        try:
            book = Book.objects.get(id=id)
            context = {'book': book}
            if request.method == "POST":
                if request.FILES:
                    os.remove(book.product_image.path)
                    book.product_image = request.FILES['image']
                book.product_name = request.POST['name']
                book.product_desc = request.POST['description']
                book.review = request.POST['review']
                book.save()
                messages.success(request, "Succesfully updated all details")
                return redirect('adminproduct')
            return render(request, 'adminview/admin-edit-product.html', context)



        except Exception as e:
            print(e)
            messages.error(request, "Saved failed")
            return redirect('admincategory')
    return redirect('adminlogin')

@cache_control(no_cache=True, no_store=True)
def admin_product(request):
    if 'email' in request.session:
        book=Book.objects.all()

        context={
            'book':book
        }
        return render(request,'adminview/adminproduct.html',context)
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='adminlogin')
def admin_add_author(request):
    if 'email' in request.session:
        try:
            if request.method=='POST':
                name=request.POST['name']
                image = request.FILES.get('image')
                description = request.POST['description']

                author=Author(author_name=name,author_image=image,author_desc=description)
                author.save()
                messages.success(request, "Succesfully added")
                return redirect("adminauthor")
        except Exception as e:
            print(e)
            messages.error(request, "Saved failed")
            return redirect("adminauthor")
        return render(request, 'adminview/adminaddauthor.html')
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
def admin_edit_author(request, id):
    if 'email' in request.session:
        context = {}
        try:
            author = Author.objects.get(id=id)
            context = {'author': author}
            if request.method == "POST":
                print(request.POST)
                if request.FILES:
                    os.remove(author.author_image.path)
                    author.author_image = request.FILES['image']
                author.author_name = request.POST['name']
                author.author_desc = request.POST['description']
                author.save()
                messages.info(request, "Succesfully updated all details")
                return redirect('adminauthor')
            return render(request, 'adminview/admin-author-edit.html', context)



        except Exception as e:
            print(e)
            return redirect('admincategory')
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
def admin_author(request):
    try:
        if 'email' in request.session:
            author = Author.objects.all()
            context = {
                'author': author
            }
            return render(request, 'adminview/adminauthor.html', context)
        return redirect('adminlogin')
    except Exception as e:
        print(e)


@cache_control(no_cache=True, no_store=True)
def admin_add_category(request):
    if 'email' in request.session:
        try:
            offer = Offer.objects.all()
            if request.method=='POST':
                name=request.POST['name']
                image = request.FILES.get('image')
                description = request.POST['description']
                offer=request.POST['offer']
                offer_obj=Offer.objects.get(id=offer)
                maxamount=request.POST['maxdiscount']
                try:
                    if offer_obj.is_expired():
                        messages.error(request, 'Offer is expired. Please select a valid offer.')
                        return redirect("admincategory")
                except Exception as e:
                    print(e)
                if Category.objects.filter(category_name=name).exists():
                    messages.error(request, 'Category with this name already exists.')
                    return redirect("admincategory")
                category=Category(category_name=name,category_image=image,category_desc=description,offer_cat=offer_obj,max_discount=maxamount)
                category.save()
                messages.error(request, 'Saved Successfully')
                return redirect("admincategory")

        except Exception as e:
            messages.error(request,'Saved failed')
            return redirect("admincategory")
        context={
            'offer':offer
        }
        return render(request, 'adminview/admin-add-category.html',context)
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
def admin_category(request):
    try:
        if 'email' in request.session:
            category = Category.objects.all()
            context = {
                'category': category
            }
            return render(request, 'adminview/admincategory.html', context)
        return redirect('adminlogin')
    except Exception as e:
        print(e)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='adminlogin')
def admin_edit_category(request, id):
    if 'email' in request.session:
        context = {}
        print("call fucntion")
        try:
            category = Category.objects.get(id=id)
            offer=Offer.objects.all()

            context = {'category': category,
                       'offer':offer}
            if request.method == "POST":
                print(request.POST)
                if request.FILES:
                    os.remove(category.category_image.path)
                    category.category_image = request.FILES['catimage']
                category.category_name = request.POST['catname']
                category.category_desc = request.POST['description']
                category_offer=request.POST['offer_cat']
                offer_obj = Offer.objects.get(id=category_offer)
                category.max_discount=request.POST['maxdiscount']
                try:
                    if offer_obj.is_expired():
                        messages.error(request, 'Offer is expired. Please select a valid offer.')
                        return redirect("admincategory")
                except Exception as e:
                    print(e)
                category.offer_cat=offer_obj
                category.offer = 12

                category.save()
                print('after save')
                messages.success(request, "Succesfully updated all details")
                return redirect('admincategory')

            return render(request, 'adminview/admin-edit-category.html', context)



        except Exception as e:
            print(e)
            return redirect('admincategory')
    return redirect('adminlogin')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='adminlogin')
def admin_delete_category(request, id):
    category=Category.objects.get(id=id)
    category.delete()
    return redirect('admincategory')
# Create your views here.

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='adminlogin')
def admin_offer_add(request):
    if 'email' in request.session:
        try:
            if request.method == 'POST':
                name = request.POST['name']
                percentage = float(request.POST['percentage'])  # Convert to float
                startdate = request.POST['startdate']
                enddate = request.POST['enddate']

                if percentage <= 70:  # Check if percentage is not greater than 70
                    offer = Offer(name=name, off_percent=percentage, start_date=startdate, end_date=enddate)
                    offer.save()
                    messages.success(request, 'Saved successfully')
                    return redirect("adminoffer")
                else:
                    messages.error(request, 'Percentage cannot be greater than 70')
                    return redirect("adminoffer")

            # If method is not POST, render the form again
            return render(request, 'adminview/admin-add-offer.html')

        except Exception as e:
            print(e)
            messages.error(request, 'Saved failed')
            return render(request, 'adminview/admin-add-offer.html')
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
def admin_offer(request):
    if 'email' in request.session:
        offer=Offer.objects.all()
        context={
            'offer':offer
        }
        return render(request,'adminview/admin-offer.html',context)
    return redirect('adminlogin')

@cache_control(no_cache=True, no_store=True)
def admin_edit_offer(request,id):
    if 'email' in request.session:
        context={}
        try:
            offer = Offer.objects.get(id=id)
            context = {'offer': offer}
            if request.method == "POST":
                offer.name = request.POST['offer_name']
                offer.off_percent = request.POST['off_percent']
                offer.start_date = request.POST['start_date']
                offer.end_date = request.POST['end_date']
                offer.save()
                messages.info(request, "Succesfully updated all details")
                return redirect('adminoffer')
        except Exception as e:
            print(e)
            messages.info(request, "Updated failed")
            return redirect('admineditoffer')

        return render(request, 'adminview/admin-edit-offer.html', context)
    return redirect('adminlogin')



@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='adminlogin')
# def add_product_variant(request):
#     if 'email' in request.session:
#         context = {}
#
#         try:
#             product = Book.objects.all().order_by('id')
#             author = Author.objects.all().order_by('id')
#             offer = Offer.objects.all().order_by('id')
#             category = Category.objects.all().order_by('id')
#             edition=Editions.objects.all().order_by('id')
#
#             if request.method == "POST":
#                 product = request.POST.get('product')
#                 category = request.POST.get('category')
#                 author = request.POST.get('author')
#                 offer = request.POST.get('offer')
#                 edition = request.POST.get('edition')
#                 price = request.POST.get('price')
#                 stock = request.POST.get('stock')
#                 rating = request.POST.get('rating')
#
#                 prod_obj = Book.objects.get(id=product)
#                 cat_obj = Category.objects.get(id=category)
#                 author_obj = Author.objects.get(id=author)
#                 offer_obj = Offer.objects.get(id=offer)
#                 edition_obj=Editions.objects.get(id=edition)
#                 print(prod_obj.product_name)
#
#                 variant_name = f"{prod_obj.product_name} {author_obj.author_name} {edition_obj.edition_name}"
#
#
#                 try:
#
#                     variant = Bookvariant.objects.get(product=prod_obj, author=author_obj,edition=edition_obj)
#
#                     messages.error(request, "Variant already exists")
#                 except Bookvariant.DoesNotExist:
#                     if Bookvariant.objects.filter(product=prod_obj, category=cat_obj).exists():
#                         messages.error(request, "This product is already selected for the category.")
#                     else:
#
#                         variant = Bookvariant(
#
#                             variant_name=variant_name,
#                             product=prod_obj,
#                             author=author_obj,
#                             category=cat_obj,
#                             edition=edition_obj,
#                             product_price=price,
#                             stock=stock,
#                             rating=rating,
#                             offer=offer_obj
#                         )
#
#                         variant.save()
#
#                     try:
#                         multiple_images = request.FILES.getlist('multipleImage', None)
#                         if multiple_images:
#                             for image in multiple_images:
#                                 photo = MultipleImages.objects.create(
#                                     product=variant,
#                                     images=image,
#                                 )
#
#                     except Exception as e:
#                         print(e)
#                         messages.info(request, "Image Upload Failed")
#                         return redirect('productaddvariant')
#
#                     messages.info(request, "Product variant saved successfully")
#                     return redirect('productaddvariant')
#
#             context = {
#                 'product': product,
#                 'author': author,
#                 'offer': offer,
#                 'category': category,
#                 'edition':edition
#             }
#
#         except Exception as e:
#             print(e)
#             return redirect('productaddvariant')
#
#         return render(request, 'adminview/admin-add-product-variant.html', context)
#     return redirect('adminlogin')

def add_product_variant(request):
    if 'email' in request.session:
        context = {}

        try:
            if request.method == "POST":
                product_id = request.POST.get('product')
                category_id = request.POST.get('category')
                author_id = request.POST.get('author')
                offer_id = request.POST.get('offer')
                edition_id = request.POST.get('edition')
                price = request.POST.get('price')
                stock = request.POST.get('stock')
                rating = request.POST.get('rating')

                prod_obj = Book.objects.get(id=product_id)
                cat_obj = Category.objects.get(id=category_id)
                author_obj = Author.objects.get(id=author_id)
                offer_obj = Offer.objects.get(id=offer_id)
                edition_obj = Editions.objects.get(id=edition_id)

                # Check if a variant with the same product and category already exists
                if Bookvariant.objects.filter(product=prod_obj).exists():
                    # Get the name of the category to which the product is already allocated
                    allocated_category = Bookvariant.objects.get(product=prod_obj).category.category_name
                    messages.error(request,
                                   f'{prod_obj.product_name} is already allocated to the category "{allocated_category}".')
                    return redirect('productaddvariant')


                else:
                    variant_name = f"{prod_obj.product_name} {author_obj.author_name} {edition_obj.edition_name}"

                    variant = Bookvariant(
                        variant_name=variant_name,
                        product=prod_obj,
                        author=author_obj,
                        category=cat_obj,
                        edition=edition_obj,
                        product_price=price,
                        stock=stock,
                        rating=rating,
                        offer=offer_obj
                    )

                    variant.save()

                # Handle multiple image upload
                try:
                    multiple_images = request.FILES.getlist('multipleImage', None)
                    if multiple_images:
                        for image in multiple_images:
                            photo = MultipleImages.objects.create(
                                product=variant,
                                images=image,
                            )
                except Exception as e:
                    print(e)
                    messages.info(request, "Image Upload Failed")

                messages.info(request, "Product variant saved successfully")
                return redirect('productaddvariant')

            # Fetch all necessary data for rendering the form
            products = Book.objects.all().order_by('id')
            authors = Author.objects.all().order_by('id')
            offers = Offer.objects.all().order_by('id')
            categories = Category.objects.all().order_by('id')
            editions = Editions.objects.all().order_by('id')

            context = {
                'product': products,
                'author': authors,
                'offer': offers,
                'category': categories,
                'edition': editions
            }

        except Exception as e:
            print(e)
            messages.error(request, "An error occurred while adding product variant.")
            return redirect('productaddvariant')

        return render(request, 'adminview/admin-add-product-variant.html', context)
    return redirect('adminlogin')


def admin_edition(request):
    if 'email' in request.session:
        edition=Editions.objects.all()
        context={
            'edition':edition
        }
        return render(request,'adminview/admin-edition.html',context)
    return redirect('adminlogin')


def admin_add_edition(request):
    if 'email' in request.session:
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST['description']
            publisher = request.POST['publisher']
            year = request.POST['year']

            edition = Editions(edition_name=name, edition_desc=description, publisher=publisher,year=year)
            edition.save()
            messages.success(request, "Succesfully saved")
            return redirect("adminedition")
        return render(request, 'adminview/admin-edition-add.html')
    return redirect('adminlogin')

@cache_control(no_cache=True, no_store=True)
def admin_edit_edition(request,id):
    if 'email' in request.session:
        context={}
        try:
            edition = Editions.objects.get(id=id)
            context = {'edition': edition}
            if request.method == "POST":

                edition.edition_name = request.POST['name']
                edition.edition_desc = request.POST['description']
                edition.publisher=request.POST.get('publisher')
                edition.year=request.POST['year']
                edition.save()
                messages.info(request, "Succesfully updated all details")
                return redirect('adminedition')


        except Exception as e:
            print(e)
            messages.info(request, "Succesfully saved")
        return render(request, 'adminview/admin-edition-edit.html', context)
    return redirect('adminlogin')


@cache_control(no_cache=True, no_store=True)
def admin_edition_action(request, id):
    user = Editions.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('adminedition')


def admin_offer_action(request,id):
    user = Offer.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('adminoffer')


@cache_control(no_cache=True, no_store=True)
def admin_variant(request):
        if 'email' in request.session:
            context = {}
            try:
                variant = Bookvariant.objects.all()
                variant_images = {}

                for image in variant:
                    images = MultipleImages.objects.filter(product=image)
                    variant_images[image.id] = list(images)
                context = {
                    'variant': variant,
                    'variant_images': variant_images
                }
            except Exception as e:
                print(e)

            return render(request, 'adminview/adminvariant.html', context)
        return redirect('adminlogin')


@cache_control(no_cache=True, no_store=True)
def admin_variant_edition_action(request, id):
    user = Bookvariant.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('adminvariant')

def admin_edit_product_variant(request, id):
    if 'email' in request.session:
        context = {}

        try:
            variant=Bookvariant.objects.get(id=id)
            print(variant.variant_name,'uu')

            product = Book.objects.all().order_by('id')
            author = Author.objects.all().order_by('id')
            offer = Offer.objects.all().order_by('id')
            category = Category.objects.all().order_by('id')
            edition = Editions.objects.all().order_by('id')
            object_image = MultipleImages.objects.filter(product=id)

            if request.method == "POST":
                product = request.POST.get('product')
                category = request.POST.get('category')
                author = request.POST.get('author')
                offer = request.POST.get('offer')
                edition = request.POST.get('edition')
                price = request.POST.get('price')
                stock = request.POST.get('stock')
                rating = request.POST.get('rating')

                prod_obj = Book.objects.get(id=product)
                cat_obj = Category.objects.get(id=category)
                author_obj = Author.objects.get(id=author)
                offer_obj = Offer.objects.get(id=offer)
                edition_obj = Editions.objects.get(id=edition)

                variant.product = prod_obj
                variant.category = cat_obj
                variant.author = author_obj
                variant.offer = offer_obj
                variant.edition = edition_obj
                variant.product_price = price
                variant.stock = stock
                variant.rating = rating

                multiple_images = request.FILES.getlist('multipleImage', None)
                if multiple_images:
                    if object_image:
                        for image in object_image:
                            os.remove(image.images.path)
                            image.delete()
                        for image in multiple_images:
                            img = MultipleImages.objects.create(
                                product=variant,
                                images=image
                            )
                    else:
                        for image in multiple_images:
                            img = MultipleImages.objects.create(
                                product=variant,
                                images=image
                            )
                variant_name = f"{prod_obj.product_name} {author_obj.author_name} {edition_obj.edition_name}"
                variant.variant_name = variant_name
                variant.save()
                messages.success(request, "Edited Successfully")
                return redirect('adminvariant')


            context = {
                'variant': variant,
                'product': product,
                'author': author,
                'offer': offer,
                'category': category,
                'edition': edition,
                'multiple_images': object_image,

            }
        except Exception as e:
            print(e)




        return render(request,'adminview/admin-edit-variant.html',context)
    return redirect('adminlogin')

def delete_image(request, image_id):
    try:

        image = MultipleImages.objects.get(id=image_id)
        variant_id = image.product.id
        image.delete()

        # Redirect back to the same page after deletion
        return redirect('adminvariantedit',id=variant_id)
    except Exception as e:
        # Handle case where image does not exist
        return redirect('adminvariantedit',id=variant_id)



def coupon_list(request):
    if 'email' in request.session:

        try:

            coupons = Coupons.objects.all()
            context = {
                'coupons': coupons,
            }
            return render(request, 'adminview/admin-coupons.html', context)
        except Coupons.DoesNotExist:
            context = {
                'coupons': None,
                'message': 'No coupons found.',
            }
            return render(request, 'adminview/admin-coupons.html', context)
    return redirect('adminlogin')

def add_coupon(request):
    if 'email' in request.session:
        try:
            if request.method == "POST":
                coupon_code = request.POST.get("coupon_code")
                min_amount = request.POST.get("min_amount")
                off_percent = request.POST.get("off_percent")
                max_discount = request.POST.get("max_discount")
                expiry_date = request.POST.get("expiry_date")
                coupon_stock = request.POST.get("coupon_stock")

                # Validate coupon_code
                if coupon_code and coupon_code.islower():
                    messages.warning(request, "Coupon code cannot contain small letters!")
                    return redirect("addcoupon")

                if Coupons.objects.filter(coupon_code=coupon_code).exists():
                    messages.warning(request, "This coupon is already in your account!")
                    return redirect("addcoupon")

                # Validate min_amount
                if not min_amount.isdigit() or int(min_amount) < 500:
                    messages.warning(request, "Minimum amount must be a number greater than or equal to 500!")
                    return redirect("addcoupon")

                # Validate off_percent
                if not off_percent.isdigit() or int(off_percent) <= 0:
                    messages.warning(request, "Off percent must be a positive number greater than 0!")
                    return redirect("addcoupon")

                # Validate max_discount
                if not max_discount.isdigit() or int(max_discount) < int(off_percent):
                    messages.warning(request, "Max discount must be a number greater than or equal to Off percent!")
                    return redirect("addcoupon")

                # Validate expiry_date
                try:
                    expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                except ValueError:
                    messages.warning(request, "Invalid expiry date format. Please use YYYY-MM-DD.")
                    return redirect("addcoupon")

                if expiry_date <= timezone.now().date():
                    messages.warning(request, "Expiry date should be in the future!")
                    return redirect("addcoupon")

                # Validate coupon_stock
                if coupon_stock:
                    try:
                        coupon_stock = int(coupon_stock)
                        if coupon_stock < 0:
                            raise ValueError
                    except ValueError:
                        messages.warning(request, "Coupon stock must be a non-negative integer!")
                        return redirect("addcoupon")
                else:
                    coupon_stock = None

                coupon = Coupons(
                    coupon_code=coupon_code,
                    min_amount=min_amount,
                    off_percent=off_percent,
                    max_discount=max_discount,
                    expiry_date=expiry_date,
                    coupon_stock=coupon_stock
                )
                coupon.save()

                messages.success(request, f"{coupon_code} added successfully!")
                return redirect("coupon")

        except Exception as e:
            print(e)
            messages.error(request, "Failed to save coupon!")
            return redirect("addcoupon")

        return render(request, "adminview/admin-add-coupon.html")
    return redirect('adminlogin')


def admin_coupon_action(request, id):
    user = Coupons.objects.get(id=id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()

    return redirect('coupon')


def admin_edit_coupon(request, id):
    try:
        coupon = Coupons.objects.get(id=id)
        if request.method == "POST":
            coupon_code = request.POST.get("coupon_code")
            min_amount = request.POST.get("min_amount")
            off_percent = request.POST.get("off_percent")
            max_discount = request.POST.get("max_discount")
            expiry_date = request.POST.get("expiry_date")
            coupon_stock = request.POST.get("coupon_stock")

            # Check if the edited coupon code is unique
            if Coupons.objects.exclude(id=id).filter(coupon_code=coupon_code).exists():
                messages.error(request, 'Coupon code must be unique.')
                return redirect('couponedit', id=id)

            # Update the coupon
            Coupons.objects.filter(id=id).update(
                coupon_code=coupon_code,
                min_amount=min_amount,
                off_percent=off_percent,
                max_discount=max_discount,
                expiry_date=expiry_date,
                coupon_stock=coupon_stock
            )
            messages.success(request, f'{coupon_code} updated successfully.')
            return redirect('coupon')

        context = {
            'coupon': coupon
        }
        return render(request, 'adminview/admin-edit-coupon.html', context)
    except Coupons.DoesNotExist:
        messages.error(request, 'Coupon does not exist.')
        return redirect('coupon')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('coupon')


def admin_orders(request):
    if 'email' in request.session:
        context = {}
        try:
            orders = Order.objects.all().order_by('-order_id')
            context = {
                'orders': orders,
            }
        except Exception as e:
            print(e)
        return render(request, 'adminview/admin-order.html', context)
    return redirect('adminlogin')





def admin_order_update(request, id):
    if 'email' in request.session:
        context = {}
        try:
            order = Order.objects.get(id=id)
            order_items = OrderProduct.objects.filter(order_id=id)
            payment = order.payment
            if request.method == 'POST':
                order_status = request.POST.get('orderStatus', None)
                if order_status:
                    order.status = order_status
                    order.save()
                if order_status == 'Delivered':
                    payment.is_paid = True
                payment.save()
                messages.success(request, 'Status updated')
                return redirect('order_update', id)
            context = {
                'order': order,
                'order_items': order_items,
            }
            return render(request, 'adminview/admin_order_update.html', context)
        except Exception as e:
            print(e)
            return redirect('adminorder')
    return redirect('adminlogin')

def admin_sales_reports(request):
    context = {}
    try:
        book = Bookvariant.objects.all()
        cancel_orders = OrderProduct.objects.filter(item_cancel=True)

        context = {
            'book': book,
            'cancel_orders': cancel_orders,
        }
    except Exception as e:
        print(e)

    return render(request, 'adminview/admin_sales_report.html', context)
