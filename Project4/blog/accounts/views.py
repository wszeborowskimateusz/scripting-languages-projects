from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


def register_view(request):
    if request.method == 'POST':
        # validate the data
        register_form = UserCreationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return redirect('accounts:login')
    else:
        register_form = UserCreationForm()
    return render(request, 'accounts/register.html', {"register_form": register_form})


def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('articles:list')
    else:
        login_form = AuthenticationForm()
    return render(request, 'accounts/login.html', {"login_form": login_form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')

