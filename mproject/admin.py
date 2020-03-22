from django.contrib import admin
from .import models
# Register your models here.
admin.site.register(models.DepartmentTable)
admin.site.register(models.TeacherTable)
admin.site.register(models.StudentTable)
admin.site.register(models.CourseTable)
admin.site.register(models.EventTable)