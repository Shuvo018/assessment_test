from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class RegisterForm(forms.ModelForm):
    password         = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        min_length=8,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
    )

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "username", "email", "role", "password", "confirm_password"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Last name"}),
            "username":   forms.TextInput(attrs={"placeholder": "Username"}),
            "email":      forms.EmailInput(attrs={"placeholder": "Email address"}),
            "role":       forms.Select(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password         = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email address", "autofocus": True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )

    error_messages = {
        "invalid_login": "Invalid email or password. Please try again.",
        "inactive":      "This account has been deactivated.",
    }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Last name"}),
        }
