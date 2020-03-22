from django.db import models
from django.contrib.auth.models import User
# Create your models here.

gender = (
    ('男', "男"),
    ('女', "女"),
)


class DepartmentTable(models.Model):  # 院系表
    department_number = models.CharField(max_length=20, primary_key=True, verbose_name='院系号')
    department_name = models.CharField(max_length=20, verbose_name='院系名称')
    department_address = models.CharField(max_length=20, verbose_name='地址')
    department_phone_number = models.CharField(max_length=20, verbose_name='联系电话')

    def get_department_name(self):
        return self.department_name


class StudentTable(models.Model):   # 学生表
    student_user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True, verbose_name='用户')
    student_name = models.CharField(max_length=20, verbose_name='姓名')
    student_gender = models.CharField(max_length=20, choices=gender, default='男', verbose_name='性别')
    student_birth = models.CharField(max_length=20, verbose_name='出生日期')
    student_native_place = models.CharField(max_length=20, verbose_name='籍贯')
    student_phone_number = models.CharField(max_length=20, verbose_name='手机号码')
    student_department = models.ForeignKey(DepartmentTable, on_delete=models.CASCADE, verbose_name='所属院系')

    def get_student_name(self):
        return self.student_name

    def get_student_number(self):
        return self.student_user.username

    def get_student_gender(self):
        return self.student_gender

    def get_student_birth(self):
        return self.student_birth

    def get_student_native_place(self):
        return self.student_native_place

    def get_student_phone_number(self):
        return self.student_phone_number

    def get_student_department_name(self):
        return self.student_department.get_department_name()


class TeacherTable(models.Model):   # 教师表
    teacher_user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True, verbose_name='用户')
    teacher_name = models.CharField(max_length=20, verbose_name='姓名')
    teacher_gender = models.CharField(max_length=20, choices=gender, default='男', verbose_name='性别')
    teacher_birth = models.CharField(max_length=20, verbose_name='出生日期')
    teacher_degree = models.CharField(max_length=20, verbose_name='学历')
    teacher_salary = models.IntegerField(verbose_name='基本工资')
    teacher_department = models.ForeignKey(DepartmentTable, on_delete=models.CASCADE, verbose_name='所属院系')

    def get_teacher_name(self):
        return self.teacher_name

    def get_teacher_number(self):
        return self.teacher_user.username

    def get_teacher_gender(self):
        return self.teacher_gender

    def get_teacher_department_name(self):
        return self.teacher_department.get_department_name()


class CourseTable(models.Model):    # 课程表
    course_number = models.CharField(max_length=20, verbose_name='课号')
    course_teacher = models.ForeignKey(TeacherTable, on_delete=models.CASCADE, verbose_name='授课教师')
    course_name = models.CharField(max_length=20, verbose_name='课名')
    course_score = models.IntegerField(verbose_name='学分')
    course_term = models.CharField(max_length=20, verbose_name='学期')
    course_times = models.CharField(max_length=20, verbose_name='上课时间')

    class Meta:
        unique_together = ("course_number", "course_teacher")

    def get_course_number(self):
        return self.course_number

    def get_course_name(self):
        return self.course_name

    def get_course_times(self):
        return self.course_times

    def get_course_score(self):
        return self.course_score

    def get_teacher_name(self):
        return self.course_teacher.get_teacher_name()

    def get_teacher_number(self):
        return self.course_teacher.get_teacher_number()


class EventTable(models.Model):     # 选课表
    event_student = models.ForeignKey(StudentTable, verbose_name='选课学生', on_delete=models.CASCADE)
    event_course = models.ForeignKey(CourseTable, verbose_name='课程', on_delete=models.CASCADE)
    event_usual_results = models.IntegerField(verbose_name='平时成绩', null=True, blank=True)
    event_exam_results = models.IntegerField(verbose_name='考试成绩', null=True, blank=True)
    event_total_results = models.IntegerField(verbose_name='总评成绩', null=True, blank=True)

    def get_student_name(self):
        return self.event_student.get_student_name()

    def get_student_number(self):
        return self.event_student.get_student_number()

    def get_course_number(self):
        return self.event_course.get_course_number()

    def get_course_name(self):
        return self.event_course.get_course_name()

    def get_teacher_name(self):
        return self.event_course.get_teacher_name()

    def get_teacher_number(self):
        return self.event_course.get_teacher_number()

    def get_course_times(self):
        return self.event_course.get_course_times()

    def get_course_score(self):
        return self.event_course.get_course_score()

    def get_usual_results(self):
        return self.event_usual_results

    def get_exam_results(self):
        return self.event_exam_results

    def get_total_results(self):
        return self.event_total_results


