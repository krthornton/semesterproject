from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from .models import NewUser, Item
from .forms import NewUserForm, ItemSearchForm, UpdateUserInfoForm


# view for the home page
def index(request):
    context = {}
    return render(request, 'app/home.html', context)


# view for managing a user's account
@login_required
@require_http_methods(['GET'])
def view_account(request):
    context = {
        'user': request.user,
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
            context = {
                'user': request.user,
                'updated': True,
            }
            return render(request, 'registration/view_account.html', context)
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
            context = {
                'user': request.user,
                'password_changed': 'success',
            }
            return render(request, 'registration/view_account.html', context)
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
@require_http_methods(['GET'])
def item_description(request, slug):
    # get requested object from DB and return info about it
    item = get_object_or_404(Item, slug=slug)
    context = {
        'item_name': item.name,
        'item_image': item.image,
        'item_desc': item.desc,
        'item_price': item.price,
        'item_stock': item.stock,
    }
    return render(request, 'app/item_description.html', context)


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
