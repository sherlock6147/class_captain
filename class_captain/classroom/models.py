from django.db import models
from base.models import generate_random_code

# Create your models here.
class Building(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6,default=generate_random_code,unique=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    floor = models.CharField(max_length=20)
    seating_capacity = models.IntegerField(default=0)
    whiteboard_available = models.BooleanField(default=False)
    projector_available = models.BooleanField(default=False)
    blackboard_available = models.BooleanField(default=False)
    ready = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.building.name + '|' + self.name
