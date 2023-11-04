from django.contrib import admin
from booking.models import Booking,BookedDate
# Register your models here.
admin.site.register(
    [BookedDate,Booking]
)