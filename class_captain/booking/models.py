from django.db import models
from base.models import (
    Student,
    Professor,
)
from classroom.models import Classroom
import pendulum

# Create your models here.

class BookedDate(models.Model):
    date = models.DateField("date of booking")

    def __str__(self) -> str:
        return "Date of Booking " + self.date.strftime("%d/%m/%Y")

class Booking(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    REPEATABLE_CHOICES = (
        ('No Repeat','No Repeat'),
        ('Repeat only on Weekdays','Repeat only on Weekdays'),
        ('Repeat only on Weekends','Repeat only on Weekends'),
        ('Repeat Daily','Repeat Daily'),
        ('Weekly','Weekly')
    )
    repeatable = models.CharField(choices=REPEATABLE_CHOICES)
    classroom = models.ForeignKey(Classroom,on_delete=models.DO_NOTHING,null=True)
    suggested_by = models.ForeignKey(Student,default=None,blank=True,null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="approved_bookings")
    booked_for = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="booking_holders")
    approval_for = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="booking_approver")
    booked_by = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="booked_bookings")
    expiry = models.DateTimeField()
    booked_dates = models.ManyToManyField(BookedDate)

    @property
    def is_approved(self):
        return self.approved_by != None
    
    def generate_booked_dates(self, save=True):
        if not self.is_approved:
            return
        start_date = self.date
        expiry = self.expiry
        expiry_date = expiry.date()
        repeat = self.repeatable
        days_for_booking = []
        if repeat == 'No Repeat':
            weekday = start_date.weekday()
            days_for_booking.append(weekday)
        elif repeat == 'Repeat only on Weekdays':
            # days_for_booking = ['Monday','Tuesday','Wednesday','Thursday','Friday']
            days_for_booking = [0,1,2,3,4]
        elif repeat == 'Repeat only on Weekends':
            # days_for_booking = ['Saturday','Sunday']
            days_for_booking = [5,6]
        elif repeat == 'Repeat Daily':
            days_for_booking = [0,1,2,3,4,5,6]
        elif repeat == 'Weekly':
            days_for_booking.append(start_date.weekday())
        current = pendulum.now()
        current.set(year = start_date.year,
                    month=start_date.month,
                    day=start_date.day)
        while current.date() <= expiry_date:
            if current.date() == expiry_date:
                if self.end_time < self.expiry.time():
                    if current.weekday() in days_for_booking:
                        date_obj,created = BookedDate.objects.get_or_create(date=current.date())
                        self.booked_dates.add(date_obj)
            else:
                if current.weekday() in days_for_booking:
                        date_obj,created = BookedDate.objects.get_or_create(date=current.date())
                        self.booked_dates.add(date_obj)
            current = current.add(days=1)
        if save:
            self.save()
        else:
            return self.booked_dates.all()

    def __str__(self) -> str:
        return self.name


def generate_unsaved_booked_dates(unsaved_booking:Booking):
    start_date = unsaved_booking.date
    expiry = unsaved_booking.expiry
    expiry_date = expiry.date()
    repeat = unsaved_booking.repeatable
    days_for_booking = []
    if repeat == 'No Repeat':
        weekday = start_date.weekday()
        days_for_booking.append(weekday)
    elif repeat == 'Repeat only on Weekdays':
        # days_for_booking = ['Monday','Tuesday','Wednesday','Thursday','Friday']
        days_for_booking = [0,1,2,3,4]
    elif repeat == 'Repeat only on Weekends':
        # days_for_booking = ['Saturday','Sunday']
        days_for_booking = [5,6]
    elif repeat == 'Repeat Daily':
        days_for_booking = [0,1,2,3,4,5,6]
    elif repeat == 'Weekly':
        days_for_booking.append(start_date.weekday())
    if not start_date.weekday() in days_for_booking:
        days_for_booking.append(start_date.weekday())
    current = pendulum.now()
    current.set(year = start_date.year,
                month=start_date.month,
                day=start_date.day)
    booked_dates = []
    while current.date() <= expiry_date:
        if current.date() == expiry_date:
            if unsaved_booking.end_time < unsaved_booking.expiry.time():
                if current.weekday() in days_for_booking:
                    booked_dates.append(current.date())
        else:
            if current.weekday() in days_for_booking:
                    booked_dates.append(current.date())
        current = current.add(days=1)
    return booked_dates