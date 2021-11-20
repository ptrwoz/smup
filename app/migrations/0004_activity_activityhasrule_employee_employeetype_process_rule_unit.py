# Generated by Django 3.2.9 on 2021-11-20 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0003_auto_20211120_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('idactivity', models.AutoField(db_column='idActivity', primary_key=True, serialize=False)),
                ('timeconsuming', models.DateTimeField(db_column='timeConsuming')),
                ('timeadd', models.DateTimeField(db_column='timeAdd')),
                ('timefrom', models.DateTimeField(blank=True, db_column='timeFrom', null=True)),
                ('timeto', models.CharField(blank=True, db_column='timeTo', max_length=45, null=True)),
            ],
            options={
                'db_table': 'activity',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('idemployee', models.AutoField(db_column='idEmployee', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('surname', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'db_table': 'employee',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Employeetype',
            fields=[
                ('idemployee_type', models.AutoField(db_column='idEmployee Type', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'db_table': 'employeetype',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('idprocess', models.AutoField(db_column='idProcess', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('tip', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'process',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('idrule', models.IntegerField(db_column='idRule', primary_key=True, serialize=False)),
                ('timefrom', models.DateTimeField(db_column='timeFrom')),
                ('timeto', models.DateTimeField(db_column='timeTo')),
            ],
            options={
                'db_table': 'rule',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('idunit', models.AutoField(db_column='idUnit', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'db_table': 'unit',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ActivityHasRule',
            fields=[
                ('activity_idactivity', models.OneToOneField(db_column='Activity_idActivity', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='app.activity')),
            ],
            options={
                'db_table': 'activity_has_rule',
                'managed': False,
            },
        ),
    ]
