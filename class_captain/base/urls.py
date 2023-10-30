from django.urls import path
from base.views import (
    home,
    profile,
    view_secret_tokens,
    delete_secret,
    add_secret,
    register_professor,
    register_student,
    edit_view,
    edit_student,
    edit_professor,
)
app_name = "base"

urlpatterns = [
    path('', home, name="home"),
    path('profile/',profile, name='profile'),
    path('secrets/view',view=view_secret_tokens,name='view_secret_tokens'),
    path('secrets/delete/<secret_id>',view=delete_secret, name='delete_secret'),
    path('secrets/add/',view=add_secret,name='add_secret'),
    path('register/prof/',view=register_professor,name="register_prof"),
    path('register/student/',view=register_student,name="register_student"),
    path('profile/edit',view=edit_view, name='profile_edit'),
    path('edit/prof/',view=edit_professor,name="edit_prof"),
    path('edit/student/',view=edit_student,name="edit_student"),
]