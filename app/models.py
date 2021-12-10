# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Activity(models.Model):
    idactivity = models.AutoField(db_column='idActivity', primary_key=True)  # Field name made lowercase.
    timeconsuming = models.FloatField(db_column='timeConsuming')  # Field name made lowercase.
    timeadd = models.DateTimeField(db_column='timeAdd')  # Field name made lowercase.
    timefrom = models.DateField(db_column='timeFrom', blank=True, null=True)  # Field name made lowercase.
    timeto = models.DateField(db_column='timeTo', blank=True, null=True)  # Field name made lowercase.
    rule_has_process_id_rule_has_process = models.ForeignKey('RuleHasProcess', models.DO_NOTHING, db_column='rule_has_process_id_rule_has_process')

    class Meta:
        managed = False
        db_table = 'activity'
        unique_together = (('idactivity', 'timeconsuming'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DataType(models.Model):
    iddata_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_type'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Employee(models.Model):
    idemployee = models.AutoField(db_column='idEmployee', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=256, blank=True, null=True)
    surname = models.CharField(max_length=256, blank=True, null=True)
    idunit = models.ForeignKey('Unit', models.DO_NOTHING, db_column='idUnit')  # Field name made lowercase.
    idemployeetype = models.ForeignKey('Employeetype', models.DO_NOTHING, db_column='idEmployeeType')  # Field name made lowercase.
    auth_user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    isactive = models.IntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employee'


class Employeetype(models.Model):
    idemployee_type = models.AutoField(db_column='idEmployee Type', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    name = models.CharField(unique=True, max_length=64)

    class Meta:
        managed = False
        db_table = 'employeetype'


class Process(models.Model):
    idprocess = models.AutoField(db_column='idProcess', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=256)
    tip = models.TextField(blank=True, null=True)
    idnumber = models.IntegerField(db_column='idNumber')  # Field name made lowercase.
    idmainprocess = models.ForeignKey('self', models.DO_NOTHING, db_column='idMainProcess', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'process'


class Rule(models.Model):
    idrule = models.AutoField(db_column='idRule', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45, blank=True, null=True)
    max = models.FloatField(blank=True, null=True)
    timefrom = models.DateField(db_column='timeFrom')  # Field name made lowercase.
    timeto = models.DateField(db_column='timeTo')  # Field name made lowercase.
    employee_idemployee = models.ForeignKey(Employee, models.DO_NOTHING, db_column='Employee_idEmployee')  # Field name made lowercase.
    time_range_idtime_range = models.ForeignKey('TimeRange', models.DO_NOTHING, db_column='time_range_idtime_range')
    data_type_iddata_type = models.ForeignKey(DataType, models.DO_NOTHING, db_column='data_type_iddata_type')

    class Meta:
        managed = False
        db_table = 'rule'


class RuleHasProcess(models.Model):
    rule_idrule = models.ForeignKey(Rule, models.DO_NOTHING, db_column='rule_idRule')  # Field name made lowercase.
    process_idprocess = models.ForeignKey(Process, models.DO_NOTHING, db_column='process_idProcess')  # Field name made lowercase.
    id_rule_has_process = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'rule_has_process'


class TimeRange(models.Model):
    idtime_range = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'time_range'


class Unit(models.Model):
    idunit = models.AutoField(db_column='idUnit', primary_key=True)  # Field name made lowercase.
    name = models.CharField(unique=True, max_length=256)

    class Meta:
        managed = False
        db_table = 'unit'
