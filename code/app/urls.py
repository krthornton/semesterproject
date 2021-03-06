from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('browse', views.browse_items, name='browse'),
    re_path(r'^item/(?P<slug>[a-z\-0-9]+)/$', views.item_description, name='description'),
    path('view_cart', views.view_cart, name='view_cart'),
    path('update_cart', views.update_cart, name='update_cart'),
    path('checkout', views.checkout, name='checkout'),
    path('view_account', views.view_account, name='view_account'),
    path('update_account', views.update_account_info, name='update_account'),
    path('change_password', views.change_password, name='change_password'),
    path('login', views.login_user, name='login'),
    path('register', views.register, name='register'),
]
