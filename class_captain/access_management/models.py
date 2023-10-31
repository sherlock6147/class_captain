from django.db import models
from base.models import(
    Professor,
    Student,
)
from classroom.models import (
    Classroom,
)
# Create your models here.
class PAG(models.Model):
    name = models.CharField(max_length=200)
    professors = models.ManyToManyField(Professor)
    classrooms = models.ManyToManyField(Classroom)

    def __str__(self) -> str:
        return self.name

class SAG(models.Model):
    name = models.CharField(max_length=200)
    students = models.ManyToManyField(Student)
    classrooms = models.ManyToManyField(Classroom)

    def __str__(self) -> str:
        return self.name