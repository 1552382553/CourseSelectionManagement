python 3.7 

django pymysql

在v1/settings.py中配置数据库信息（DATABASES）



运行：

在主目录下

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser 

​	（创建管理员账号和密码，邮箱可以不填）

python manage.py runserver 8003



使用：登录管理员账号创建老师、学生、学院，之后可以由老师和学生账号登录