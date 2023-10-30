from django.db import models
from class_captain.users.models import User
import random
import string
from django.db import models
import pendulum
from config.settings.base import TIME_ZONE


def generate_random_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

# Create your models here.
class Department(models.Model):
    name = models.CharField()
    short = models.CharField("abbreviation")

    def __str__(self) -> str:
        return self.name + '| '+self.short

class Student(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    mobile = models.CharField(max_length=10)
    roll = models.CharField("Roll No.",max_length=10)
    reg = models.CharField("Registration No.",max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'Student: '+ self.user.name + '| '+self.department.name + '|' +self.reg

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'Professor: '+self.user.name + '| '+self.department.name

class SecretToken(models.Model):
    TOKEN_TYPES = (
        ('Student','Student'),
        ('Professor','Professor'),
    )
    code = models.CharField(max_length=6, default=generate_random_code, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)

    def __str__(self):
        return self.code + '| '+ self.token_type

    @property
    def status(self):
        expired = False
        if not self.expiry:
            expired = False
        now = pendulum.now(TIME_ZONE)
        expired = self.expiry < now;
        if expired:
            return "EXPIRED"
        else:
            return "ACTIVE"