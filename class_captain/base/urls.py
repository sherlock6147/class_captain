from django.urls import path
from base.views import (
    home,
    profile,
    view_secret_tokens,
    delete_secret,
    add_secret,
)
app_name = "base"

urlpatterns = [
    path('', home, name="home"),
    path('profile/',profile, name='profile'),
    path('secrets/view',view=view_secret_tokens,name='view_secret_tokens'),
    path('secrets/delete/<secret_id>',view=delete_secret, name='delete_secret'),
    path('secrets/add/',view=add_secret,name='add_secret')
]