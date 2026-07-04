from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm


def get_post_login_redirect(user):
    if user.is_teacher:
        return "dashboard"
    return "student_dashboard"


def register_view(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect(request.user))

    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect(get_post_login_redirect(user))
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect(request.user))

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(get_post_login_redirect(user))
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("login")
    return redirect("profile")


@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html", {"user": request.user})


@login_required
def profile_view(request):
    user = request.user
    editing = request.method == "POST" or request.GET.get("edit") == "1"
    form = ProfileForm(request.POST or None, instance=user) if editing else None

    if request.method == "POST" and form is not None and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")

    return render(request, "accounts/profile.html", {
        "form": form,
        "user": user,
        "editing": editing,
    })