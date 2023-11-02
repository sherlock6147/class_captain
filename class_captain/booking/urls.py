from django.urls import path
from booking.views import (
    list_all,
    add_booking,
    edit_booking,
    approve_booking,
    delete_booking,
    detail_view,
)
app_name = "booking"

urlpatterns = [
    path('', list_all, name="list_all"),
    path('add/<classroom_id>',add_booking, name='add'),
    path('delete/<booking_id>',view=delete_booking,name='delete'),
    path('edit/<booking_id>',view=edit_booking, name='edit'),
    path('approve/<booking_id>',view=approve_booking, name='approve'),
    path('view/classroom/<classroom_id>',view=detail_view,name="classroom_booking_detail")
]