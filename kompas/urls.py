"""kompas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from info.views import index
from user.views import profile_view, top_up, edit_data, passport, get_money, top_down, find_friends, add_friend, \
    delete_friend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', profile_view, name='profile'),
    path('profile/edit', edit_data, name='edit'),
    path('profile/friends', find_friends, name='friends'),
    path('profile/top_up/', top_up, name='top_up'),
    path('profile/top_down/', top_down, name='top_down'),
    path('profile/add_passport', passport, name='passport'),
    path('auth/', include('user.urls')),
    path('profile/get', get_money, name='get_money'),
    path('', index, name='root'),
    path('add_friend/<int:id>/', add_friend, name='add_friend'),
    path('delete_friend/<int:id>/', delete_friend, name='delete_friend'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

