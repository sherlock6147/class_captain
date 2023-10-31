from django.urls import path
from classroom.views import (
    list_all,
    add_classroom,
    edit_classroom,
    delete_classroom,
    detail_view,
)
app_name = "booking"

urlpatterns = [
    path('', list_all, name="list_all"),
    path('add/',add_classroom, name='add'),
    path('delete/<classroom_id>',view=delete_classroom,name='delete'),
    path('edit/<classroom_id>',view=edit_classroom, name='edit'),
    path('view/<classroom_id>',view=detail_view,name="detail")
]