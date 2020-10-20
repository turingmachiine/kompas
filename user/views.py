import functools
import json
import os
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy

from info.models import MoneyLogs
from social_api.ConfigAPI import ConfigAPI
from social_api.InstagramInitializer import InstagramInitializer
from user.forms import LoginForm, RegisterForm, ForgotForm, PasswordForm, VerifyForm, EditForm, PassportForm, MoneyForm
from user.models import User, Passport, Follow


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect(reverse('root'))
            else:
                return render(
                    request, "login.html",
                    {"form": form, "errors": ["Incorrect login or password or you need to confirm your account"]})
        else:
            return render(request, "login.html", {"form": form})
    else:
        if request.user.is_authenticated:
            return redirect(reverse('profile'))
        form = LoginForm()
        return render(request, "login.html", {"form": form})


@login_required(login_url=reverse_lazy('login'))
def logout_view(request):
    logout(request)
    return redirect(reverse("login"))


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                fathers_name=form.cleaned_data["fathers_name"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"])
            user.save()
            # send_email.delay("Confirm Email", settings.DEFAULT_FROM_EMAIL, user.email,
            #                  'mail.html', args=dict(code=user.confirm_code, name=user.first_name))
            return redirect(reverse("login"))
        else:
            if request.user.is_authenticated:
                return redirect(reverse('profile'))
            return render(request, "register.html", {"form": form})
    else:
        return render(request, "register.html", {"form": RegisterForm()})


def forgot(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('profile'))
        form = ForgotForm()
        return render(request, "forgot.html", {"form": form})
    elif request.method == "POST":
        form = ForgotForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                token = uuid.uuid4()
                user.confirm_code = token
                user.save()
                # send_email.delay("Reset password", settings.DEFAULT_FROM_EMAIL, user.email,
                #                  'mail-reset.html', args=dict(code=user.confirm_code, name=user.first_name))
            except User.DoesNotExist:
                return render(
                    request, "forgot.html",
                    {"form": form, "errors": ["This email is wrong"]})
            return render(request, "forgot_success.html", {})


def reset(request, code):
    success = False
    if request.method == "GET":
        try:
            user = User.objects.get(confirm_code=code)
            form = PasswordForm()
        except User.DoesNotExist:
            return redirect(reverse('root'))
        except ValidationError:
            return redirect(reverse('root'))
        return render(request, "reset.html", {"form": form, "code": code})
    elif request.method == "POST":
        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(confirm_code=code)
                user.set_password(form.cleaned_data['password'])
                user.save()
                return redirect(reverse("login"))
            except User.DoesNotExist:
                pass
        else:
            render(request, "reset.html", {"form": form, "code": code})


def make_borrower_distinct(income_debt):
    result = dict()
    for item in income_debt:
        if not item['borrower__username'] in result.keys():
            result[item['borrower__username']] = dict()
        if not item['date'] in result[item['borrower__username']].keys():
            result[item['borrower__username']][item['date']] = item['sum']
        else:
            result[item['borrower__username']][item['date']] += item['sum']
    return result


def make_source_distinct(outcome_debt):
    result = dict()
    for item in outcome_debt:
        if not item['source__username'] in result.keys():
            result[item['source__username']] = dict()
        if not item['date'] in result[item['source__username']].keys():
            result[item['source__username']][item['date']] = item['sum']
        else:
            result[item['source__username']][item['date']] += item['sum']
    return result


@login_required(login_url=reverse_lazy('login'))
def profile_view(request):
    user = request.user
    print(user.friends.exists())
    income_debt = MoneyLogs.objects.filter(source=user, borrower__isnull=False).values('sum', 'borrower__username',
                                                                                       'date')
    income_debt = make_borrower_distinct(income_debt)
    outcome_debt = MoneyLogs.objects.filter(borrower=user, source__isnull=False).values('sum', 'source__username',
                                                                                        'date')
    outcome_debt = make_source_distinct(outcome_debt)
    print(income_debt)
    print(outcome_debt)
    return render(request, "profile.html", {"user": user, "income_debt": income_debt, "outcome_debt": outcome_debt})


@login_required(login_url=reverse_lazy('login'))
def get_money(request):
    user = request.user
    if user.friends.exists():
        limit = functools.reduce(lambda x, y: x + y, user.friends.values_list("balance", flat=True))
        if request.method == "POST":
            form = MoneyForm(request.POST)
            if form.is_valid():
                money = form.cleaned_data["money"]
                if money < limit:
                    amount = money
                    friends = user.friends.filter(balance__gt=0)
                    sums = dict()
                    for friend in friends:
                        sums[friend.id] = 0
                    while abs(amount) > 1E-7:
                        friends = user.friends.filter(balance__gt=0)
                        count = friends.count()
                        iter_contribution = amount / count
                        for friend in friends:
                            if friend.balance >= iter_contribution:
                                sums[friend.id] += iter_contribution
                                friend.balance -= iter_contribution
                                friend.save()
                                amount -= iter_contribution
                            else:
                                sums[friend.id] += friend.balance
                                amount -= friend.balance
                                friend.balance = 0
                                friend.save()
                    user.balance += money
                    user.save()
                    for key in sums.keys():
                        MoneyLogs.objects.create(source_id=key, borrower=user, sum=sums[key], operation="LOAN")
                    return redirect("profile")
                elif money == limit:
                    for friend in user.friends:
                        MoneyLogs.objects.create(borrower=user, source=friend, sum=friend.balance, operation="LOAN")
                        friend.balance = 0
                        friend.save()
                    user.balance += limit
                    user.save()
                    return redirect("profile")
                else:
                    return render(request, "get_money.html", {"user": user, "limit": limit, "form": MoneyForm()})

        else:
            return render(request, "get_money.html", {"user": user, "limit": limit, "form": MoneyForm()})
    else:
        return redirect("profile")

@login_required(login_url=reverse_lazy('login'))
def edit_data(request):
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.fathers_name = form.cleaned_data["fathers_name"]
            user.credit_card_number = form.cleaned_data["credit_card_number"]
            if user.vk_link != form.cleaned_data["vk_link"]:
                if form.cleaned_data["vk_link"] is not None and form.cleaned_data["vk_link"].find(
                        "vk.com") != -1:
                    config = ConfigAPI()
                    config.init()
                    query = form.cleaned_data["vk_link"].split("/")[3]
                    vk_user = config.api.users.get(user_ids=query, fields="id")
                    user_id = vk_user[0]["id"]
                    friends = config.api.friends.get(user_id=user_id, fields="id, domain")
                    for friend in friends["items"]:
                        friend_model = User.objects.filter(
                            vk_link__contains="vk.com/{}".format(friend["domain"])).first()
                        if friend_model is not None:
                            follow = Follow.objects.get_or_create(follower=user, follow_user=friend_model)
                            follow = Follow.objects.get_or_create(follower=friend_model, follow_user=user)
                user.vk_link = form.cleaned_data["vk_link"]
            if user.instagram_link != form.cleaned_data["instagram_link"]:
                if form.cleaned_data["instagram_link"] is not None and form.cleaned_data["instagram_link"].find(
                        "instagram.com") != -1:
                    # init = InstagramInitializer()
                    # friends = init.get_friends(form.cleaned_data["instagram_link"].split("/")[3])
                    pass
                user.instagram_link = form.cleaned_data["instagram_link"]

            user.email = form.cleaned_data["email"]
            user.save()
            return redirect("profile")
        else:
            return render(request, "edit.html", {"user": request.user, "form": EditForm()})
    else:
        user = request.user
        return render(request, "edit.html", {"user": user, "form": EditForm()})


@login_required(login_url=reverse_lazy('login'))
def top_up(request):
    user = request.user
    user.balance += 1000
    user.save()
    MoneyLogs.objects.create(borrower=user, sum=1000, operation="REPLENISHMENT")
    return redirect(reverse('profile'))


@login_required(login_url=reverse_lazy('login'))
def passport(request):
    if request.method == "POST":
        form = PassportForm(request.POST)
        if form.is_valid():
            passport = Passport.objects.create(number=form.cleaned_data["number"], series=form.cleaned_data["series"],
                                               when=form.cleaned_data["when"], who=form.cleaned_data["who"],
                                               code_who=form.cleaned_data["code_who"])
            request.user.passport = passport
            request.user.save()
            return redirect("profile")
    else:
        user = request.user
        return render(request, "passport.html", {"user": user, "form": PassportForm()})
