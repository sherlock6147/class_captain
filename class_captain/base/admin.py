from django.contrib import admin
from base.models import (
    Department,
    Student,
    Professor,
    SecretToken
)
# Register your models here.
admin.site.register(
    [Department,Student,Professor,SecretToken]
)