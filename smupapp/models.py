# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

appName = 'smupapp'

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
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
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
    id_data_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        
        db_table = '{}_datatype'.format(appName)

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

class Activity(models.Model):
    id_activity = models.AutoField(primary_key=True)
    value = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)
    time_add = models.DateTimeField(blank=True, null=True)
    time_from = models.DateField()
    time_to = models.DateField()
    rule_has_process_id_rule_has_process = models.ForeignKey('RuleHasProcess', models.DO_NOTHING, db_column='rule_has_process_id_rule_has_process')
    employee_id_employee = models.ForeignKey('Employee', models.DO_NOTHING, db_column='employee_id_employee')
    class Meta:
        db_table = '{}_activity'.format(appName)

class Employee(models.Model):
    id_employee = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    surname = models.CharField(max_length=256, blank=True, null=True)
    id_unit = models.ForeignKey('Unit', models.DO_NOTHING, db_column='id_unit')
    id_employeetype = models.ForeignKey('Employeetype', models.DO_NOTHING, db_column='id_employeetype')
    auth_user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        db_table = '{}_employee'.format(appName)


class Employeetype(models.Model):
    id_employeetype = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    class Meta:
        db_table = '{}_employeetype'.format(appName)

class Process(models.Model):
    id_process = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    tip = models.TextField(blank=True, null=True)
    id_number = models.IntegerField()
    id_mainprocess = models.ForeignKey('self', models.DO_NOTHING, db_column='id_mainProcess', blank=True, null=True)  # Field name made lowercase.
    order = models.IntegerField(default=-1)
    number = models.CharField(max_length=256, default='')
    class Meta:
        db_table = '{}_process'.format(appName)
    def __str__(self):
        return str(self.id_process) + " " + self.name


class Rule(models.Model):
    id_rule = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    max_value = models.FloatField(null = True, blank = True, default = 0)
    time_from = models.DateField()
    time_to = models.DateField()
    time_range = models.ForeignKey('TimeRange', models.DO_NOTHING)
    data_type = models.ForeignKey(DataType, models.DO_NOTHING)
    is_active = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = '{}_rule'.format(appName)


class RuleHasEmployee(models.Model):
    id_rule_has_employee = models.BigAutoField(primary_key=True)
    rule_id_rule = models.ForeignKey(Rule, models.DO_NOTHING, db_column='rule_id_rule')
    employee_id_employee = models.ForeignKey(Employee, models.DO_NOTHING, db_column='employee_id_employee')
    class Meta:
        db_table = '{}_rulehasemployee'.format(appName)

class RuleHasProcess(models.Model):
    process_id_process = models.ForeignKey(Process, models.DO_NOTHING, db_column='process_id_process')
    id_rule_has_process = models.BigAutoField(primary_key=True)
    rule_id_rule = models.ForeignKey(Rule, models.DO_NOTHING, db_column='rule_id_rule')
    class Meta:
        db_table = '{}_rulehasprocess'.format(appName)


class TimeRange(models.Model):
    id_time_range = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        db_table = '{}_timerange'.format(appName)


class Unit(models.Model):
    id_unit = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=256)
    is_active = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = '{}_unit'.format(appName)