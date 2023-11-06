from django.contrib import admin
from .models import User, Task

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff',
    ]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'id','task_heading','creation_date', 'last_modified','task_owner','task_complete'
    ]
