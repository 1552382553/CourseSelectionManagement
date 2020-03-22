"""v1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mproject import views
urlpatterns = [
    # 管理员
    path('admin/', admin.site.urls),
    # common
    path('', views.link_empty),
    path('home/', views.link_home),
    path('login/', views.link_login),
    path('logout/', views.link_logout),
    path('index/', views.link_index),
    path('changepassword/', views.link_change_password),
    path('dropschool/', views.link_drop_school),
    # student
    path('selectcourse/', views.link_student_select_course),
    path('dropcourse/', views.link_student_drop_course),
    path('querycourse/', views.link_student_query_course),
    path('queryresults/', views.link_student_query_results),
    # teacher
    path('opencourse/', views.link_teacher_open_course),
    path('deletecourse/', views.link_teacher_delete_course),
    path('coursecondition/', views.link_teacher_course_condition),
    path('manageresults/', views.link_teacher_manage_results),
]
