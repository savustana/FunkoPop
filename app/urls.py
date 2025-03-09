"""
URL configuration for FunkoPj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views, admin

urlpatterns = [

    path('', views.index, name='index'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register, name='register'),
    path('add_new_item/', views.add_new_item, name='add_new_item'),
    path('add_category/', views.add_new_category, name='add_new_category'),
    path('cart/', views.view_cart, name='view_cart'),
    path('stats/', views.stats, name='stats'),
    path('delete/', views.delete_cart_items, name='delete_cart_items'),
    path('item_page/<int:item_id>', views.item_page, name='item_page'),
    path('data/', views.serialize_data, name='serialize_data'),
]
