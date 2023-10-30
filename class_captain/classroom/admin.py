from django.contrib import admin
from classroom.models import(
    Building,
    Classroom
)
# Register your models here.
admin.site.register(
    [
        Building,
        Classroom
        ]
)