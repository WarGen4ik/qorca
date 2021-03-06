# Generated by Django 2.0.4 on 2018-04-03 19:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_main', '0010_auto_20180403_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/no-img.png', upload_to='avatars/', verbose_name='Avatar'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(null=True, verbose_name='Birth date'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='city',
            field=models.CharField(max_length=100, null=True, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.SmallIntegerField(choices=[(1, 'male'), (2, 'female')], default=1, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(max_length=20, null=True, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.SmallIntegerField(choices=[(1, 'user'), (2, 'manager')], default=1, verbose_name='Role'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Administrator'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=255, verbose_name='Last name'),
        ),
    ]
