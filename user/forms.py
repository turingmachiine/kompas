from django import forms

from user.models import User, Passport


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class ForgotForm(forms.Form):
    email = forms.EmailField(label="Enter your email to reset password")


class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = {"username", "first_name", "last_name", "fathers_name", "email", "password",
                  "vk_link", "instagram_link"}

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()


class PasswordForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = {"password"}

    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()


class VerifyForm(forms.ModelForm):
    class Meta:
        model = Passport
        exclude = {}


class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = {"first_name", "email", "last_name", "fathers_name", "credit_card_number", "vk_link", "instagram_link"}


class PassportForm(forms.ModelForm):
    class Meta:
        model = Passport
        exclude = {}


class MoneyForm(forms.Form):
    money = forms.FloatField()
