from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import NON_FIELD_ERRORS

from .models import NewUser, Item, ShoppingCartItem
from .forms import NewUserForm, ItemSearchForm, UpdateUserInfoForm,\
                   NewShoppingCartItemForm, RemoveCartItemForm,\
                   ConfirmCheckoutForm


# shows the user the home page along with the recently added shoes
def index(request):
    context = {
        'user': request.user,
        'items': Item.objects.order_by('date_added'),
    }
    return render(request, 'app/home.html', context)


# view for managing a user's account
@login_required
@require_http_methods(['GET'])
def view_account(request):
    context = {
        'user': request.user,
        'cart_items': ShoppingCartItem.objects.filter(user_key=request.user),
    }
    return render(request, 'registration/view_account.html', context)


# view for updating information about a user's account
@login_required
@require_http_methods(['GET', 'POST'])
def update_account_info(request):
    if request.method == 'POST':
        # if this is a POST, user has submitted updated information
        form = UpdateUserInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            # if valid, redirect to view_account and re-login the user
            form.save()
            messages.add_message(request, messages.INFO, "User information updated!")
            return redirect('/view_account')
        else:
            # form is not valid, notify user
            context = {
                'user': request.user,
                'form': form,
            }
            return render(request, 'registration/update_account.html', context)
    else:
        form = UpdateUserInfoForm()
        context = {
            'user': request.user,
            'form': form,
        }
        return render(request, 'registration/update_account.html', context)


# view for changing a user's password
@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        # user has submitted a new password
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # password is good; save and re-login the user
            user = form.save()
            update_session_auth_hash(request, user)
            messages.add_message(request, messages.INFO, "User password changed!")
            return redirect('/view_account')
        else:
            # password is bad, notify user
            context = {
                'form': form,
            }
            return render(request, 'registration/change_password.html', context)
    else:
        # this is a GET request, display password change form
        form = PasswordChangeForm(request.user)
        context = {
            'form': form,
        }
        return render(request, 'registration/change_password.html', context)


# view for creating new users
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'GET':
        # send a blank form for the user to fill in
        form = NewUserForm()
        context = {
            'form': form,
        }
        return render(request, 'registration/register.html', context)
    elif request.method == 'POST':
        # create a new user from the form and log them in
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = NewUser.objects.create_user(**form.cleaned_data)
            user.save()
            login(request, user)
        return index(request)


# view for viewing a specific item
@require_http_methods(['GET', 'POST'])
def item_description(request, slug):
    if request.method == 'POST':
        # double check that user is authenticated
        if not request.user.is_authenticated:
            # if the user isn't logged in, redirect to login page
            messages.add_message(request, messages.ERROR, "You must be logged in to add to cart.")
            return redirect('/accounts/login')
        # if this is a POST request, user is adding to their cart
        item = get_object_or_404(Item, slug=slug)
        form = NewShoppingCartItemForm(request.POST)
        if form.is_valid():
            # save the form to add item to the user's cart; notify user of success
            form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully added %s to your shopping cart." % item.name)
        else:
            if form.has_error(NON_FIELD_ERRORS, 'unique_together'):
                # user must already have the item in their cart; notify the user
                messages.add_message(request, messages.INFO, "This item is already in your cart!")
            else:
                # an unknown error occurred; notify the user
                messages.add_message(request, messages.ERROR, "An unknown error occurred.")
        return redirect('/item/%s' % slug)
    else:
        # this must be a GET request, get requested object from DB and return info about it
        item = get_object_or_404(Item, slug=slug)
        context = {
            'item': item,
            'user': request.user,
        }
        return render(request, 'app/item_description.html', context)


# view for displaying a user's shopping cart
@login_required
@require_http_methods(['GET', 'POST'])
def view_cart(request):
    if request.method == 'POST':
        # if this is a POST request, validate form
        form = RemoveCartItemForm(request.POST)
        form.full_clean()
        if form.cleaned_data['item_key'] and form.cleaned_data['user_key']:
            # remove requested item from user's shopping cart
            cart_item = ShoppingCartItem.objects.get(item_key=form.cleaned_data['item_key'],
                                                     user_key=form.cleaned_data['user_key'])
            item_name = cart_item.item_key.name
            cart_item.delete()
            messages.add_message(request, messages.SUCCESS, "Successfully removed %s" % item_name)
            return redirect('/view_cart')
        else:
            # something went wrong, notify user
            messages.add_message(request, messages.ERROR, "Error: invalid form")
            return redirect('/view_cart')
    else:
        # this must be a GET request, display user's shopping cart
        context = {
            'user': request.user,
            'cart_items': ShoppingCartItem.objects.filter(user_key=request.user)
        }
        return render(request, 'registration/view_cart.html', context)


# view for checking out the user's shopping cart
@login_required
@require_http_methods(['GET', 'POST'])
def checkout(request):
    if request.method == 'POST':
        # if this is a POST request, validate form
        form = ConfirmCheckoutForm(request.POST, instance=request.user)
        if form.is_valid():
            # if the form is valid, save form to update user information
            form.save()
            # remove all items from user's shopping cart
            for cart_entry in ShoppingCartItem.objects.filter(user_key=request.user):
                cart_entry.delete()
            # add message to notify user of checkout success; redirect to view account
            messages.add_message(request, messages.SUCCESS, "Successfully checked out!")
            return redirect('/view_account')
        else:
            # something went wrong if the form is invalid, notify the user
            messages.add_message(request, messages.ERROR, "invalid form")
            return redirect('/checkout')
    else:
        # this must be a GET request; calculate subtotal and give user form
        subtotal = 0
        for cart_entry in ShoppingCartItem.objects.filter(user_key=request.user):
            subtotal += cart_entry.item_key.price * cart_entry.quantity
        form = ConfirmCheckoutForm()
        context = {
            'user': request.user,
            'form': form,
            'subtotal': round(subtotal, 2),
            'cart_items': ShoppingCartItem.objects.filter(user_key=request.user),
        }
        return render(request, 'registration/checkout.html', context)


# view for browsing/searching for items
@require_http_methods(['GET', 'POST'])
def browse_items(request):
    if request.method == 'POST':
        # if POST, search with given search term
        form = ItemSearchForm(request.POST)
        if form.is_valid():
            # if form is valid, return search results
            items = Item.objects.filter(name__contains=form.cleaned_data['name'])
            context = {
               'items': items,
            }
            return render(request, 'app/browse.html', context)
        else:
            # invalid form
            for field in form:
                for error in field.errors:
                    if error == "This field is required.":
                        # user submitted an empty search
                        context = {
                            'errors': [
                                "Error: Empty search.",
                            ],
                        }
                        return render(request, 'app/browse.html', context)
    else:
        # if GET, just display search
        return render(request, 'app/browse.html', {})
