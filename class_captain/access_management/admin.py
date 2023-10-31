from django.contrib import admin
from access_management.models import (
    PAG,
    SAG,
)
# Register your models here.
admin.site.register(
    [PAG,SAG]
)