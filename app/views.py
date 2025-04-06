from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .form import NewUserForm, StuffForm, CategoryForm, SeriesForm, ProfileUserForm
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from .models import Stuff, User, Category, Order, ProfileUser, Series, StuffOrder
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib.auth.decorators import user_passes_test, login_required

from .serializers import FunkoSerializer, UserSerializer
from django.http import JsonResponse
from django.core.paginator import Paginator

context = dict()


def admin_check(user):
    return user.is_staff


def index(request):
    base_context(request)
    stuff_list = Stuff.objects.all()
    context.update({'stuff_list': stuff_list})

    if request.method == "POST" and request.user:
        item_id = request.POST['add_to_cart']
        item = Stuff.objects.filter(pk=item_id).first()
        stuff_order, created = StuffOrder.objects.get_or_create(item=item, defaults={'quantity': 1})

        order, order_created = Order.objects.get_or_create(user=request.user)
        current_stuff = StuffOrder.objects.filter(id=stuff_order.id).first()
        order.items.add(current_stuff)

        if not stuff_order:
            return HttpResponse("StuffOrder not found", status=404)

        if not order:
            return HttpResponse("Order not found", status=404)

        if not created:
            stuff_order.quantity += 1

        stuff_order.save()
        order.total_price += item.price
        order.save()

        return redirect(view_cart)

    return render(request, 'index.html', context=context)


def pop_page(request):
    base_context(request)
    stuff_list = Stuff.objects.filter(category=1).all()
    context.update({'stuff_list': stuff_list})
    pop = Category.objects.filter(id=1).first()
    context.update({'pop': pop})

    if request.method == "POST" and request.user:
        item_id = request.POST['add_to_cart']
        item = Stuff.objects.filter(pk=item_id).first()
        # stuff_order = StuffOrder.objects.filter(item=item).first()
        stuff_order = StuffOrder.objects.get_or_create(item=item)

        if not stuff_order:
            stuff_order = StuffOrder.objects.create(item=item)

        price = item.price
        order = Order.objects.filter(user=request.user).first()
        order.total_price += price
        stuff_order.quantity += 1
        order.items.add(stuff_order)
        order.save()
        stuff_order.save()

        return redirect(view_cart)

    return render(request, 'Categories/pop_category.html', context=context)


def accessories_page(request):
    base_context(request)
    stuff_list = Stuff.objects.filter(category=2).all()
    context.update({'stuff_list': stuff_list})
    pop = Category.objects.filter(id=2).first()
    context.update({'pop': pop})

    if request.method == "POST" and request.user:
        item_id = request.POST['add_to_cart']
        item = Stuff.objects.filter(pk=item_id).first()
        stuff_order = StuffOrder.objects.filter(item=item).first()

        if stuff_order is None:
            stuff_order = StuffOrder.objects.create(item=item)

        price = item.price
        order = Order.objects.filter(user=request.user).first()
        order.total_price += price
        stuff_order.quantity += 1
        order.items.add(stuff_order)
        order.save()
        stuff_order.save()

        return redirect(view_cart)

    return render(request, 'Categories/accessories.html', context=context)


def clothing_page(request):
    base_context(request)
    stuff_list = Stuff.objects.filter(category=3).all()
    context.update({'stuff_list': stuff_list})
    pop = Category.objects.filter(id=3).first()
    context.update({'pop': pop})

    if request.method == "POST" and request.user:
        item_id = request.POST['add_to_cart']
        item = Stuff.objects.filter(pk=item_id).first()
        stuff_order = StuffOrder.objects.filter(item=item).first()

        if not stuff_order:
            stuff_order = StuffOrder.objects.create(item=item)

        price = item.price
        order = Order.objects.filter(user=request.user).first()
        order.total_price += price
        stuff_order.quantity += 1
        order.items.add(stuff_order)
        order.save()
        stuff_order.save()

        return redirect(view_cart)

    return render(request, 'Categories/clothing.html', context=context)


def base_context(request):
    context.clear()
    category = Category.objects.all()
    if request.user.is_authenticated:
        profile = ProfileUser.objects.filter(user=request.user).first()
        context.update({'profile': profile})

    MEDIA_URL = settings.MEDIA_URL
    context.update({'categories': category})
    context.update({'MEDIA_URL': MEDIA_URL})


def item_page(request, item_id):
    item = Stuff.objects.get(id=item_id)
    base_context(request)
    context.update({'item': item})

    return render(request, 'Management/item_page.html', context)


def register(request):
    base_context(request)
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # profile = ProfileUser.objects.create(user=user)
            # profile.save()
            messages.success(request, 'Your account has been created!')
            return redirect('index')
        messages.error(request, 'Please correct the error below.')
    form = NewUserForm()
    context.update({'register_form': form})
    return render(request, 'SignIn/register.html', context)


def login_page(request):
    base_context(request)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You are now logged in!')

                request.session.set_test_cookie()

                request.session.test_cookie_worked()

                request.session['username'] = username
                request.session['visits'] = request.session.get('visits', 0) + 1
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the error below.')

    form = AuthenticationForm()
    context.update({'login_form': form})
    return render(request, 'SignIn/login.html', context)


def logout_page(request):
    logout(request)
    messages.info(request, 'You have been logged out!')
    return redirect('index')


@user_passes_test(admin_check, login_url="/login/" )
def add_new_item(request):
    if request.method == 'POST':
        stuff = StuffForm(request.POST, request.FILES)
        if stuff.is_valid():
            stuff = stuff.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {'form': stuff}
            return render(request, 'AdminAccess/new_item.html', context)
    else:
        stuff = StuffForm()
        profile = ProfileUser.objects.filter(user=request.user).first()
        MEDIA_URL = settings.MEDIA_URL
        context = {'form': stuff, 'profile': profile, 'MEDIA_URL': MEDIA_URL}

        return render(request, 'AdminAccess/new_item.html', context)


@user_passes_test(admin_check, login_url="/login/" )
def add_new_category(request):
    if request.method == 'POST':
        category = CategoryForm(request.POST, request.FILES)
        if category.is_valid():
            category = category.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {'form': category}
            return render(request, 'AdminAccess/add_category.html', context)
    else:
        category = CategoryForm()
        profile = ProfileUser.objects.filter(user=request.user).first()
        MEDIA_URL = settings.MEDIA_URL
        context = {'form': category, 'profile': profile, 'MEDIA_URL': MEDIA_URL}
        return render(request, 'AdminAccess/add_category.html', context)


@user_passes_test(admin_check, login_url="/login/" )
def add_new_series(request):
    if request.method == 'POST':
        series = SeriesForm(request.POST, request.FILES)
        if series.is_valid():
            series = series.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {'form': series}
            return render(request, 'AdminAccess/add_series.html', context)
    else:
        series = SeriesForm()
        profile = ProfileUser.objects.filter(user=request.user).first()
        MEDIA_URL = settings.MEDIA_URL
        context = {'form': series, 'profile': profile, 'MEDIA_URL': MEDIA_URL}
        return render(request, 'AdminAccess/add_series.html', context)


@login_required
def view_cart(request):
    cart = Order.objects.filter(user=request.user).first()
    items = cart.items.all()
    base_context(request)
    context.update({'items_cart': items, 'cart': cart})
    if request.method == "POST" :
        if "delete_from_cart" in request.POST:
            item_id = request.POST['delete_from_cart']
            item = Stuff.objects.filter(pk=item_id).first()

            stuff_order = StuffOrder.objects.filter(item=item_id).first()
            cart.items.remove(stuff_order)

            order = StuffOrder.objects.filter(item=item_id).delete()
            cart.total_price -= stuff_order.quantity * item.price
            stuff_order.quantity = 0
            stuff_order.save()
            cart.save()


        elif 'add_to_cart' in request.POST:
            item_id = request.POST['add_to_cart']
            item = Stuff.objects.filter(pk=item_id).first()

            stuff_order = StuffOrder.objects.filter(item=item_id).first()

            stuff_order.quantity += 1
            cart.total_price += item.price
            cart.save()
            stuff_order.save()

        elif "minus_from_cart" in request.POST:
            item_id = request.POST['minus_from_cart']
            item = Stuff.objects.filter(pk=item_id).first()

            stuff_order = StuffOrder.objects.filter(item=item_id).first()

            stuff_order.quantity -= 1
            cart.total_price -= item.price
            stuff_order.save()
            cart.save()

    return render(request, 'Management/cart.html', context)


@login_required
def edit_user_profile(request):
    base_context(request)
    user_p = ProfileUser.objects.filter(user_id=request.user.id)
    context.update({'info': user_p})
    return render(request, 'UserInfo/user_profile.html', context)



@user_passes_test(admin_check, login_url="/login/" )
def stats(request):
    username = request.session.get('username')
    visits = request.session.get('visits', 0)
    return HttpResponse(f"Name: {username}, Visits: {visits}")


def delete_session(request):
    try:
        request.session.flush()
        del request.session['username']
        del request.session['visits']
    except KeyError:
        pass
    return HttpResponse("Session Deleted")


@user_passes_test(admin_check, login_url="/login/")
def serialize_data(request):
    if request.method == 'GET':
        funko = Stuff.objects.all()
        serialize_funko = FunkoSerializer(funko, many=True)

        users = User.objects.all()
        serialize_users = UserSerializer(users, many=True)
        data = [serialize_funko.data, serialize_users.data]

        return JsonResponse(data, safe=False)


@user_passes_test(admin_check, login_url="/login/")
def delete_management(request):
    base_context(request)
    stuff = Stuff.objects.all()
    category = Category.objects.all()
    series = Series.objects.all()
    context.update({
        'stuff': stuff,
        'category': category,
        'series': series,
    })

    if request.method == "POST" and 'delete_stuff' in request.POST:
        item_id = request.POST.get('delete_stuff')
        Stuff.objects.filter(id=item_id).delete()

    if request.method == "POST" and 'delete_category' in request.POST:
        item_id = request.POST.get('delete_category')
        Category.objects.filter(id=item_id).delete()

    if request.method == "POST" and 'delete_series' in request.POST:
        item_id = request.POST.get('delete_series')
        Series.objects.filter(id=item_id).delete()


    return render(request, 'AdminAccess/delete_items.html', context)


@user_passes_test(admin_check, login_url="/login/")
def users_management(request):
    base_context(request)
    users = ProfileUser.objects.all()

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_object = paginator.page(page_number)

    context.update({'page_object': page_object})


    return render(request, 'AdminAccess/users_management.html', context)


@login_required
def user_profile(request, user_id):
    profile = ProfileUser.objects.filter(user_id=user_id).first()
    base_context(request)
    context.update({'profile': profile, 'MEDIA_URL': settings.MEDIA_URL})

    if request.method == 'POST' and 'profile_submit' in request.POST:
        profile_id = request.POST.get('profile_submit')
        profile = ProfileUser.objects.filter(id=profile_id).first()
        image = request.FILES.get('profile_avatar')
        bio = request.POST.get('profile_bio')
        if image:
            profile.avatar = image
        if bio:
            profile.bio = bio
        profile.save()
        return redirect('view_profile', user_id=profile.user_id)

    return render(request, 'UserInfo/user_profile.html', context)


@login_required
def view_profile(request, user_id):
    profile = ProfileUser.objects.filter(user_id=user_id).first()
    base_context(request)
    context.update({'profile': profile, 'MEDIA_URL': settings.MEDIA_URL})
    return render(request, 'UserInfo/view_profile.html', context)

