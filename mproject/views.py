from django.shortcuts import render
from django.contrib.auth import authenticate
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import connection
cursor = connection.cursor()


# ___________________________________________________________________________common
# common_url
def link_home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/index')
    return render(request, 'home.html')


def link_empty(request):
    return HttpResponseRedirect('/home')


def link_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/index')
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            student = User.objects.get(username=username).studenttable_set.first()
            teacher = User.objects.get(username=username).teachertable_set.first()
            """
            cursor.execute("select u.id, student_name "
                           "from auth_user as u, mproject_studenttable as s "
                           "where u.id = s.student_user_id and u.username = %s" % username)
            student = cursor.fetchall()[0]

            cursor.execute("select u.id, teacher_name "
                           "from auth_user as u, mproject_teachertable as s "
                           "where u.id = s.teacher_user_id and u.username = %s" % username)
            teacher = cursor.fetchall()[0]
            """
            login(request, user)

            if student is not None:
                request.session['username'] = username
                request.session['identity'] = 'student'
                request.session['name'] = student.get_student_name()
                return HttpResponseRedirect('/index')
            elif teacher is not None:
                request.session['username'] = username
                request.session['identity'] = 'teacher'
                request.session['name'] = teacher.get_teacher_name()
                return HttpResponseRedirect('/index')
            else:
                return HttpResponseRedirect('/admin')
        else:
            return render(request, 'home.html', context={'message': "用户名或密码错误"})
    return HttpResponseRedirect('/home')


@login_required
def link_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required
def link_index(request):
    if request.session.get('identity') == 'student':
        return student_index(request)
    elif request.session.get('identity') == 'teacher':
        return teacher_index(request)
    elif request.user.is_superuser is True:
        return HttpResponseRedirect('/admin')


@login_required
def link_change_password(request):
    if request.user.is_superuser is True:
        return HttpResponseRedirect('/admin')
    context = {}
    if request.method == 'POST':
        old_password = request.POST["old_password"]
        new1_password = request.POST["new1_password"]
        new2_password = request.POST["new2_password"]
        user = authenticate(username=request.session.get('username'), password=old_password)
        if user is not None:
            if new1_password == new2_password:
                user.set_password(new2_password)
                user.save()
                return render(request, 'home.html', context={'message': "修改密码成功！"})
            else:
                context['message'] = '两次输入密码不一致！'
        else:
            context['message'] = '原密码错误！'

    return render(request, request.session.get('identity') + '_change_password.html', context=context)


@login_required
def link_drop_school(request):
    if request.user.is_superuser is True:
        return HttpResponseRedirect('/admin')
    context = {}
    if request.method == 'POST':
        old1_password = request.POST["old1_password"]
        old2_password = request.POST["old2_password"]
        user = authenticate(username=request.session.get('username'), password=old1_password)
        if user is not None and old1_password == old2_password:
            context['message'] = '请作最后确认！！！！'
        else:
            context['message'] = '密码错误！'

    return render(request, request.session.get('identity') + '_drop_school.html', context=context)


# ___________________________________________________________________________student
# student_url
@login_required
def link_student_select_course(request):
    if request.session.get('identity') != 'student':
        return link_index(request)

    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == "POST":
        message = []
        for i in range(1, 5):
            course_number = request.POST['course_number_' + str(i)]
            teacher_number = request.POST['teacher_number_' + str(i)]
            dic = {'idx': i, 'course_number': course_number, 'teacher_number': teacher_number}

            if len(course_number) == 0 and len(teacher_number) == 0:
                ret = '未填写'
            elif len(course_number) == 0:
                ret = '课程号不能为空！'
            elif len(teacher_number) == 0:
                ret = '教师号不能为空！'
            else:
                course = CourseTable.objects.filter(course_number=course_number,
                                                    course_teacher__teacher_user__username=teacher_number).first()
                """
                cursor.execute("select c.id "
                               "from mproject_teachertable as t, auth_user as u, mproject_coursetable as c "
                               "where t.teacher_user_id = u.id and c.course_teacher_id = t.teacher_user_id "
                               "and u.username = %s and c.course_number = %s" % (teacher_number, course_number))
                course1 = cursor.fetchall()
                print(course1)
                """
                if course is None:
                    ret = '此课程不存在！'
                else:
                    is_selected = EventTable.objects.filter(
                        event_course=course,
                        event_student__student_user__username=request.session.get('username')).first()
                    """
                    cursor.execute(
                        "select event_course_id "
                        "from mproject_eventtable as e, auth_user as u "
                        "where e.event_student_id = u.id and u.username = %s and e.event_course_id = %s"
                        % (request.session.get('username'), course1[0][0]))
                    event = cursor.fetchall()
                    print(event)
                    """
                    if is_selected is None:
                        ret = '选课成功！'

                        EventTable(event_course=course,
                                   event_student=StudentTable.objects.get(
                                       student_user__username=request.session.get('username'))).save()
                        """
                        cursor.execute("select id from auth_user "
                                       "where username = %s" % request.session.get('username'))
                        student_id = cursor.fetchall()[0]
                        
                        cursor.execute("insert into mproject_eventtable(event_course_id, event_student_id) "
                                       "values (%s, %s)" % (event[0][0], student_id))
                        """
                    else:
                        ret = '已选此课程！'
            dic['ret'] = ret
            message.append(dic)
        context['message'] = message
    context['student_course_all'] = student_get_course_all(request.session.get('username'))
    return render(request, 'student_select_course.html', context=context)


@login_required
def link_student_drop_course(request):
    if request.session.get('identity') != 'student':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == 'POST':
        message = []
        for i in range(1, 5):
            course_number = request.POST['course_number_' + str(i)]
            teacher_number = request.POST['teacher_number_' + str(i)]
            dic = {'idx': i, 'course_number': course_number, 'teacher_number': teacher_number}

            if len(course_number) == 0 and len(teacher_number) == 0:
                ret = '未填写'
            elif len(course_number) == 0:
                ret = '课程号不能为空！'
            elif len(teacher_number) == 0:
                ret = '教师号不能为空！'
            else:
                course = CourseTable.objects.filter(course_number=course_number,
                                                    course_teacher__teacher_user__username=teacher_number).first()
                if course is None:
                    ret = '此课程不存在！'
                else:
                    is_selected = EventTable.objects.filter(
                        event_course=course,
                        event_student__student_user__username=request.session.get('username')).first()
                    if is_selected is None:
                        ret = '未选该课程！'
                    else:
                        ret = '退课成功！'
                        is_selected.delete()
            dic['ret'] = ret
            message.append(dic)
        context['message'] = message
    context['student_course_selected'] = student_get_course_selected(request.session.get('username'))
    return render(request, 'student_drop_course.html', context=context)


@login_required
def link_student_query_course(request):
    if request.session.get('identity') != 'student':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == 'POST':
        ret = CourseTable.objects.all()
        if request.POST['course_name']:
            ret = ret.filter(course_name=request.POST['course_name'])
        if request.POST['course_number']:
            ret = ret.filter(course_number=request.POST['course_number'])
        if request.POST['course_score']:
            ret = ret.filter(course_score=request.POST['course_score'])
        if request.POST['course_times']:
            ret = ret.filter(course_times=request.POST['course_times'])
        if request.POST['teacher_name']:
            ret = ret.filter(course_teacher__teacher_name=request.POST['teacher_name'])
        if request.POST['teacher_number']:
            ret = ret.filter(course_teacher__teacher_user__username=request.POST['teacher_number'])
        context['student_course_queried'] = \
            [{'course_number': item.get_course_number(), 'course_name': item.get_course_name(),
              'teacher_number': item.get_teacher_number(), 'teacher_name': item.get_teacher_name(),
              'course_score': item.get_course_score(), 'course_times': item.get_course_times()}
             for item in ret]
    return render(request, 'student_query_course.html', context=context)


@login_required
def link_student_query_results(request):
    if request.session.get('identity') != 'student':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username'),
               'student_course_selected': student_get_course_selected(request.session.get('username'))}
    return render(request, 'student_query_results.html', context=context)


# student function
def student_index(request):
    student = User.objects.get(username=request.session.get('username')).studenttable_set.first()
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username'),
               'student_number': student.get_student_number(), 'student_name': student.get_student_name(),
               'student_gender': student.get_student_gender(),
               'student_department_name': student.get_student_department_name(),
               'student_native_place': student.get_student_native_place(),
               'student_phone_number': student.get_student_phone_number(),
               'student_course_selected': student_get_course_selected(request.session.get('username'))}
    return render(request, 'student_index.html', context=context)


def student_get_course_selected(username):
    """
    cursor.execute("select event_course_id, event_usual_results, event_exam_results, event_total_results "
                   "from mproject_eventtable as e, auth_user as u "
                   "where e.event_student_id = u.id and u.username = %s" % username)
    courses = cursor.fetchall()
    for course in courses:
        cursor.execute("select username, teacher_name, course_score, course_times "
                       "from mproject_teachertable as t, auth_user as u, mproject_coursetable as c "
                       "where t.teacher_user_id = u.id and c.course_teacher_id = t.teacher_user_id "
                       "and c.id = %s" % course[0])
        teacher = cursor.fetchall()[0]
        print(course, teacher)
    """
    course_selected = EventTable.objects.filter(
        event_student=User.objects.get(username=username).studenttable_set.first())
    return [{'course_number': item.get_course_number(), 'course_name': item.get_course_name(),
             'teacher_number': item.get_teacher_number(), 'teacher_name': item.get_teacher_name(),
             'course_score': item.get_course_score(), 'course_times': item.get_course_times(),
             'usual_results': item.get_usual_results(), 'exam_results': item.get_exam_results(),
             'total_results': item.get_total_results()}
            for item in course_selected]


def student_get_course_all(username):
    course_all = CourseTable.objects.filter()
    return [{'course_number': item.get_course_number(), 'course_name': item.get_course_name(),
             'teacher_number': item.get_teacher_number(), 'teacher_name': item.get_teacher_name(),
             'course_score': item.get_course_score(), 'course_times': item.get_course_times(),
             'course_is_selected': EventTable.objects.filter(
                 event_student=User.objects.get(username=username).studenttable_set.first(),
                 event_course=item).first() is not None}
            for item in course_all]


# ___________________________________________________________________________teacher
# teacher_url
@login_required
def link_teacher_open_course(request):
    if request.session.get('identity') != 'teacher':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == 'POST':
        message = []
        for i in range(1, 2):
            course_number = request.POST['course_number_' + str(i)]
            teacher_number = request.session.get('username')
            course_name = request.POST['course_name_' + str(i)]
            dic = {'idx': i, 'course_number': course_number, 'course_name': course_name}
            course = CourseTable.objects.filter(course_number=course_number,
                                                course_teacher__teacher_user__username=teacher_number).first()
            if course is not None:
                dic['ret'] = '课程号重复！'
            else:
                dic['ret'] = '开课成功！'
                CourseTable(course_number=course_number, course_name=course_name, course_term='冬季',
                            course_score=request.POST['course_score_' + str(i)],
                            course_times=request.POST['course_times_' + str(i)],
                            course_teacher=TeacherTable.objects.filter(
                                teacher_user__username=teacher_number).first()).save()

            message.append(dic)
        context['message'] = message
    context['teacher_course_opened'] = teacher_get_course_opened(request.session.get('username'))
    return render(request, 'teacher_open_course.html', context=context)


@login_required
def link_teacher_delete_course(request):
    if request.session.get('identity') != 'teacher':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == 'POST':
        message = []
        for i in range(1, 2):
            course_number = request.POST['course_number_' + str(i)]
            teacher_number = request.session.get('username')
            dic = {'idx': i, 'course_number': course_number}
            course = CourseTable.objects.filter(course_number=course_number,
                                                course_teacher__teacher_user__username=teacher_number).first()
            if course is not None:
                dic['ret'] = '取消开课成功！'
                course.delete()
            else:
                dic['ret'] = '课程未开设！取消失败！'

            message.append(dic)
        context['message'] = message
    context['teacher_course_opened'] = teacher_get_course_opened(request.session.get('username'))
    return render(request, 'teacher_delete_course.html', context=context)


@login_required
def link_teacher_course_condition(request):
    if request.session.get('identity') != 'teacher':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username'),
               'teacher_course_opened': teacher_get_course_opened(request.session.get('username'))}
    return render(request, 'teacher_course_condition.html', context=context)


@login_required
def link_teacher_manage_results(request):
    if request.session.get('identity') != 'teacher':
        return link_index(request)
    context = {'user_info': request.session.get('name') + '@' + request.session.get('username')}
    if request.method == 'POST':
        if request.POST.get('front_pos') is not None:
            context['front_pos'] = request.POST['front_pos']
        message = []
        for i in range(1, 2):
            course_number = request.POST['course_number_'+str(i)]
            student_number = request.POST['student_number_'+str(i)]
            teacher_number = request.session.get('username')
            usual_results = request.POST['usual_results_'+str(i)]
            exam_results = request.POST['exam_results_'+str(i)]
            total_results = request.POST['total_results_'+str(i)]

            dic = {'course_number': course_number, 'student_number': student_number,
                   'usual_results': usual_results, 'exam_results': exam_results, 'total_results': total_results}
            course = CourseTable.objects.filter(course_number=course_number,
                                                course_teacher__teacher_user__username=teacher_number).first()
            if course is not None:
                event = EventTable.objects.filter(event_course=course,
                                                  event_student__student_user__username=student_number).first()
                if event is not None:
                    flag = True
                    if usual_results is not None:
                        if usual_results.isdigit() is True and 0 <= int(usual_results) <= 100:
                            event.event_usual_results = usual_results
                        else:
                            flag = False
                            dic['ret'] = '成绩输入有误！'
                    if exam_results is not None:
                        if flag and exam_results.isdigit() is True and 0 <= int(exam_results) <= 100:
                            event.event_exam_results = exam_results
                        else:
                            flag = False
                            dic['ret'] = '成绩输入有误！'
                    if total_results is not None:
                        if flag and total_results.isdigit() is True and 0 <= int(total_results) <= 100:
                            event.event_total_results = total_results
                        else:
                            flag = False
                            dic['ret'] = '成绩输入有误！'
                    if flag:
                        event.save()
                        dic['ret'] = '成绩录入成功！'
                else:
                    dic['ret'] = '此同学未选择该课程！'
            else:
                dic['ret'] = '不存在该课程！'
            message.append(dic)
        context['message'] = message
    context['teacher_course_opened'] = teacher_get_course_opened(request.session.get('username'))
    return render(request, 'teacher_manage_results.html', context=context)


# teacher function
def teacher_index(request):
    teacher = User.objects.get(username=request.session.get('username')).teachertable_set.first()
    context = {'user_info': teacher.get_teacher_number() + '@' + teacher.get_teacher_name(),
               'teacher_number': teacher.get_teacher_number(), 'teacher_name': teacher.get_teacher_name(),
               'teacher_gender': teacher.get_teacher_gender(),
               'teacher_department_name': teacher.get_teacher_department_name(),
               'teacher_course_opened': teacher_get_course_opened(request.session.get('username'))}
    return render(request, 'teacher_index.html', context=context)


def teacher_get_course_opened(username):
    course_opened = CourseTable.objects.filter(
        course_teacher=User.objects.get(username=username).teachertable_set.first())
    ret = []
    for item in course_opened:
        dic = {'course_number': item.get_course_number(), 'course_name': item.get_course_name(),
               'course_score': item.get_course_score(), 'course_times': item.get_course_times(),
               'idx': 'idx' + item.get_course_number() + item.get_teacher_number()}
        selected_student = EventTable.objects.filter(event_course=item)
        dic['course_selected_number'] = len(selected_student)
        dic['course_selected_student'] = []
        for student in selected_student:
            dic['course_selected_student'].append({'student_number': student.get_student_name(),
                                                   'student_name': student.get_student_number(),
                                                   'usual_results': student.get_usual_results(),
                                                   'exam_results': student.get_exam_results(),
                                                   'total_results': student.get_total_results()})
        ret.append(dic)
    return ret
