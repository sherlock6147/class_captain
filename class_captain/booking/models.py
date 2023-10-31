from django.db import models
from base.models import (
    Student,
    Professor,
)
import pendulum

# Create your models here.
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
    )
    repeatable = models.CharField(choices=REPEATABLE_CHOICES)
    suggested_by = models.ForeignKey(Student,default=None,blank=True,null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="approved_bookings")
    booked_by = models.ForeignKey(Professor,default=None,blank=True,null=True, on_delete=models.SET_NULL,related_name="booked_bookings")
    expiry = models.DateTimeField()

    @property
    def is_approved(self):
        return self.approved_by != None

    def __str__(self) -> str:
        return self.name