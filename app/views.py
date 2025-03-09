from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .form import NewUserForm, FunkoPopForm, CategoryForm
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from .models import FunkoPop, Cart, User, Category
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.contrib.auth.decorators import user_passes_test, login_required

from .serializers import FunkoSerializer, UserSerializer
from django.http import JsonResponse

from rest_framework.response import Response



def admin_check(user):
    return user.is_staff



def index(request):
    funko_list = FunkoPop.objects.all()
    context = {
        'funko_list': funko_list,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    if request.method == "POST" and request.user:
        item_id = request.POST['add_to_cart']
        person_id = request.user
        items = FunkoPop.objects.get(id=item_id)
        cart, created = Cart.objects.get_or_create(item=items, user=person_id)
        if not created:
            cart.quantity += 1
        cart.save()

        return redirect(index)
    return render(request, 'index.html', context)


def item_page(request, item_id):
    item = FunkoPop.objects.get(id=item_id)


    return render(request, 'Management/item_page.html', {'item': item})


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created!')
            return redirect('index.html')
        messages.error(request, 'Please correct the error below.')
    form = NewUserForm()
    return render(request, 'SignIn/register.html', {'register_form': form})


def login_page(request):
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

    return render(request, 'SignIn/login.html', {'login_form': form})



def logout_page(request):
    logout(request)
    messages.info(request, 'You have been logged out!')
    return redirect('index')


@user_passes_test(admin_check, login_url="/login/" )
def add_new_item(request):
    if request.method == 'POST':
        funko = FunkoPopForm(request.POST, request.FILES)
        if funko.is_valid():
            funko = funko.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {'form': funko}
            return render(request, 'AdminAccess/new_item.html', context)
    else:
        funko = FunkoPopForm()
        context = {'form': funko}
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
        context = {'form': category}
        return render(request, 'AdminAccess/add_category.html', context)





@receiver(post_delete, sender=FunkoPop)
def delete_cart_items(sender, instance, **kwargs):
    Cart.objects.filter(item=instance).delete()


@login_required
def add_to_cart(request):
    if request.method == "POST":
        item_id = request.POST['add_to_cart']
        person_id = request.user.id

        cart, created = Cart.objects.get_or_create(stuff_id=item_id, person_id=person_id)
        if not created:
            cart.quantity += 1
        cart.save()

    return redirect('index')

@login_required
def view_cart(request):
    cart = Cart.objects.filter(user_id=request.user.id)

    media_url = settings.MEDIA_URL

    if request.method == "POST" and 'delete_item' in request.POST:
        item_id = request.POST['delete_item']

        cart_item = Cart.objects.get(id=item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return render(request, 'Management/cart.html',
                  {'cart': cart, 'MEDIA_URL': media_url})


@receiver(post_delete, sender=FunkoPop)
def delete_cart_items(sender, instance, **kwargs):
    cart_item = Cart.objects.get(id=instance.cart_item.item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()



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


@user_passes_test(admin_check, login_url="/login/" )
def serialize_data(request):
    if request.method == 'GET':
        funko = FunkoPop.objects.all()
        serialize_funko = FunkoSerializer(funko, many=True)

        users = User.objects.all()
        serialize_users = UserSerializer(users, many=True)
        data = [serialize_funko.data, serialize_users.data]

        return JsonResponse(data, safe=False)
