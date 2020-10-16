from django.urls import path, re_path

from user.views import login_view, logout_view, register, forgot, reset

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('forgot/', forgot, name='forgot'),
    re_path(r'reset/(?P<code>\w+)/$', reset, name='reset')
]
