from django.urls import path
from access_management.views import(
    list_PAG,
    list_SAG,
    add_PAG,
    add_SAG,
    edit_SAG,
    edit_PAG,
    delete_SAG,
    delete_PAG,
    view_SAG,
    view_PAG,
)
app_name = "access"

urlpatterns = [
    path('pags/', list_PAG, name="list_PAG"),
    path('pags/add/',add_PAG, name='add_PAG'),
    path('pags/delete/<pag_id>',view=delete_PAG,name='delete_PAG'),
    path('pags/edit/<pag_id>',view=edit_PAG, name='edit_PAG'),
    path('pags/<pag_id>',view=view_PAG,name="view_PAG"),
    path('sags/', list_SAG, name="list_SAG"),
    path('sags/add/',add_SAG, name='add_SAG'),
    path('sags/delete/<sag_id>',view=delete_SAG,name='delete_SAG'),
    path('sags/edit/<sag_id>',view=edit_SAG, name='edit_SAG'),
    path('sags/<sag_id>',view=view_SAG,name="view_SAG"),
    
]