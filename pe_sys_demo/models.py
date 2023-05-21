# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

GENDER = ((0,'男'),(1,'女'))

class Account(models.Model):
    TYPE = ((0,'管理员'),(1,'体检用户'),(2,'医务人员'))

    uid = models.AutoField(primary_key=True)
    idnum = models.CharField(max_length=18, verbose_name='身份证号', unique=True)
    pwd = models.CharField(max_length=63, verbose_name='密码')
    atype = models.SmallIntegerField(verbose_name='账户类型', choices=TYPE)

    def __str__(self):
        return str(self.uid)


class User(models.Model):
    MARRIAGE = ((0,'未婚'),(1,'已婚'))

    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=80, verbose_name='姓名')
    phone = models.CharField(max_length=15, verbose_name='手机号')
    gender = models.SmallIntegerField(choices=GENDER, verbose_name='性别', default=0)
    marriage = models.SmallIntegerField(choices=MARRIAGE, verbose_name='婚姻状况', default=0)
    dep = models.CharField(max_length=50, verbose_name='所属科室')
    career = models.CharField(max_length=80, verbose_name='工作岗位')
    factor = models.CharField(max_length=128, verbose_name='有害因素')

    def __str__(self):
        return self.name


class Staff(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=80, verbose_name='姓名')
    gender = models.SmallIntegerField(choices=GENDER, verbose_name='性别', default=0)
    phone = models.CharField(max_length=15, verbose_name='手机号')

    def __str__(self):
        return self.name


class ItemType(models.Model):
    index = models.PositiveIntegerField(verbose_name='序号', unique=True)
    name = models.CharField(max_length=64, verbose_name='类别名称', unique=True)
    # item_set

    def __str__(self):
        return self.name


class Diagnose(models.Model):
    value = models.CharField(max_length=64, verbose_name='诊断结果', unique=True)

    def __str__(self) -> str:
        return self.value


class Item(models.Model):
    item_cates = ((0,'数值型'),(1,'非数值型'))

    item_id = models.AutoField(primary_key=True)
    item = models.CharField(max_length=80, verbose_name='项目名称')
    itype = models.ForeignKey(ItemType, on_delete=models.CASCADE, verbose_name='所属类别')
    cate = models.IntegerField(choices=item_cates, default=0, verbose_name='结果类型')

    ref = models.ForeignKey(Diagnose, on_delete=models.SET_NULL, verbose_name='正常值', null=True)

    low_lmt = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='参考值下限', null=True)
    high_lmt = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='参考值上限', null=True)
    unit = models.CharField(max_length=10, verbose_name='单位')
    
    def __str__(self):
        return self.item


class Event(models.Model):
    status_choice = ((0,'可编辑'),(1,'已锁定'),(2,'已存档'))

    eid = models.AutoField(primary_key=True)
    time = models.DateTimeField(verbose_name='安排时间')
    desc = models.TextField(max_length=300, verbose_name='备注')
    status = models.SmallIntegerField(choices=status_choice, verbose_name='状态', default=0)
    # userevent_set


class UserEvent(models.Model):
    status_choice = ((0,'未完成'),(1,'已完成'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='体检事件')
    status = models.SmallIntegerField(choices=status_choice , verbose_name='状态', default=0)
    review = models.TextField(verbose_name='处置意见')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, verbose_name='主检医师', null=True)
    # record_set


class Record(models.Model):
    signs = ((0,'低'),(1,''),(2,'高'))

    userevent = models.ForeignKey(UserEvent, on_delete=models.CASCADE, verbose_name='体检事件')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='体检项目')
    rec = models.CharField(max_length=64, verbose_name='体检结果')
    sign = models.SmallIntegerField(choices=signs, verbose_name='异常情况', default=1)
