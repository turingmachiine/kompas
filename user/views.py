import functools
import json
import os
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy

from social_api.ConfigAPI import ConfigAPI
from social_api.InstagramInitializer import InstagramInitializer
from user.forms import LoginForm, RegisterForm, ForgotForm, PasswordForm, VerifyForm, EditForm, PassportForm, MoneyForm
from user.models import User, Passport, Follow, MoneyLogs


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
        if not item['destination__username'] in result.keys():
            result[item['destination__username']] = dict()
        if not item['date'] in result[item['destination__username']].keys():
            result[item['destination__username']][item['date']] = item['sum']
        else:
            result[item['destination__username']][item['date']] += item['sum']
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
    # print(user.friends.exists())
    # income_debt = MoneyLogs.objects.filter(source=user, destination__isnull=False).exclude(operation="WITHDRAWAL").values('sum', 'destination__username',
    #                                                                                    'date')
    # income_debt = make_borrower_distinct(income_debt)
    # outcome_debt = MoneyLogs.objects.filter(destination=user, source__isnull=False).exclude(operation="WITHDRAWAL").values('sum', 'source__username',
    #                                                                                     'date')
    # outcome_debt = make_source_distinct(outcome_debt)
    # print(income_debt)
    # print(outcome_debt)
    # print(user.borrowers)
    # print(user.follows)
    # for i, item in enumerate(user.follows):
    #     print("{} {}".format(i, item))
    print(user.can_pay_debt)
    return render(request, "profile.html", {"user": user})


@login_required(login_url=reverse_lazy('login'))
def get_money(request):
    user = request.user
    if user.borrowers.exists() and user.is_confirmed and (not user.has_current_debts):
        limit = functools.reduce(lambda x, y: x + y, user.borrowers.values_list("balance", flat=True))
        if request.method == "POST":
            form = MoneyForm(request.POST)
            if form.is_valid():
                money = form.cleaned_data["money"]
                if money < limit:
                    amount = money
                    friends = user.borrowers.filter(balance__gt=0)
                    sums = dict()
                    for friend in friends:
                        sums[friend.id] = 0
                    while abs(amount) > 1E-7:
                        friends = user.borrowers.filter(balance__gt=0)
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
                        MoneyLogs.objects.create(source_id=key, destination=user, sum=sums[key], operation="LOAN")
                    return redirect("profile")
                elif money == limit:
                    for friend in user.borrower:
                        MoneyLogs.objects.create(destination=user, source=friend, sum=friend.balance, operation="LOAN")
                        friend.balance = 0
                        friend.save()
                    user.balance += limit
                    user.save()
                    return redirect("profile")
                else:
                    return render(request, "get_money.html", {"user": user, "limit": limit, "borrowers": enumerate(user.borrowers), "form": MoneyForm()})

        else:
            return render(request, "get_money.html", {"user": user, "limit": limit, "borrowers": enumerate(user.borrowers), "form": MoneyForm()})
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
                # if form.cleaned_data["vk_link"] is not None and form.cleaned_data["vk_link"].find(
                #         "vk.com") != -1:
                #     config = ConfigAPI()
                #     config.init()
                #     query = form.cleaned_data["vk_link"].split("/")[3]
                #     vk_user = config.api.users.get(user_ids=query, fields="id")
                #     user_id = vk_user[0]["id"]
                #     friends = config.api.friends.get(user_id=user_id, fields="id, domain")
                #     for friend in friends["items"]:
                #         friend_model = User.objects.filter(
                #             vk_link__contains="vk.com/{}".format(friend["domain"])).first()
                #         if friend_model is not None:
                #             follow = Follow.objects.get_or_create(follower=user, follow_user=friend_model)
                #             follow = Follow.objects.get_or_create(follower=friend_model, follow_user=user)
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
    if request.method == 'POST':
        form = MoneyForm(request.POST)
        if form.is_valid():
            user = request.user
            user.balance += int(form.cleaned_data['money'])
            user.save()
            MoneyLogs.objects.create(destination=user, sum=int(form.cleaned_data['money']), operation="REPLENISHMENT")
            return redirect(reverse('profile'))
        else:
            return render(request, "add_money.html", {"user": request.user})
    else:
        return render(request, "add_money.html", {"user": request.user})


@login_required(login_url=reverse_lazy('login'))
def top_down(request):
    if request.method == 'POST':
        form = MoneyForm(request.POST)
        if form.is_valid():
            user = request.user
            user.balance -= int(form.cleaned_data['money'])
            user.save()
            MoneyLogs.objects.create(destination=user, sum=int(form.cleaned_data['money']), operation="WITHDRAWAL")
            return redirect(reverse('profile'))
        else:
            return render(request, "remove_money.html", {"user": request.user})
    else:
        return render(request, "remove_money.html", {"user": request.user})


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
            errors = form.errors
            user = request.user
            return render(request, "passport.html", {"user": user, "form": PassportForm()})
    else:
        user = request.user
        return render(request, "passport.html", {"user": user, "form": PassportForm()})


@login_required(login_url=reverse_lazy('login'))
def find_friends(request):
    if request.method == 'GET':
        name = request.GET.get("query")
        user = request.user
        if name is not None and name != '':
            users = User.objects.filter(~Q(id=user.id) & (Q(first_name__contains=name) | Q(last_name__contains=name)
                                        | Q(fathers_name__contains=name) | Q(username__contains=name)))
        else:
            users = []
            if user.vk_link is not None and user.vk_link != '':
                config = ConfigAPI()
                config.init()
                query = user.vk_link.split("/")[3]
                vk_user = config.api.users.get(user_ids=query, fields="id")
                user_id = vk_user[0]["id"]
                friends = config.api.friends.get(user_id=user_id, fields="id, domain")
                for friend in friends["items"]:
                    friend_model = User.objects.filter(
                        vk_link__contains="vk.com/{}".format(friend["domain"])).first()
                    if friend_model is not None:
                        users.append(friend_model)
        p = Paginator(users, 2)
    if request.GET.get("page") is not None:
        page = request.GET.get("page")
    else:
        page = 1

    return render(request, "friends.html", {"user": user, "users": p.page(page).object_list,
                                            "page": page, "next_page": int(page) + 1, "prev_page": int(page) - 1,
                                            "hasNextPage": p.page(page).has_next(),
                                            "hasPrevPage": p.page(page).has_previous(),
                                            "num_pages": p.num_pages,
                                            "follows": enumerate(user.follows), "borrowers": enumerate(user.borrowers)
                                            })


@login_required(login_url=reverse_lazy('login'))
def add_friend(request, id):
    Follow.objects.create(follower_id=request.user.id, follow_user_id=id)
    return redirect(reverse("friends"))


@login_required(login_url=reverse_lazy('login'))
def delete_friend(request, id):
    Follow.objects.filter(follower_id=request.user.id, follow_user_id=id).first().delete()
    return redirect(reverse("friends"))


@login_required(login_url=reverse_lazy('login'))
def return_debt(request):
    user = request.user
    if user.can_pay_debt:
        user.return_debt()
        return redirect(reverse("profile"))
    else:
        return redirect(reverse("profile"))