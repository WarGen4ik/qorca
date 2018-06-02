import datetime

import math
import random
import string

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
import django.utils.timezone


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a second name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name='admin',
            last_name='admin',
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        _('Email'),
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        _('First name'),
        max_length=255
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=255
    )
    created_at = models.DateTimeField(_('Created at'), default=django.utils.timezone.now)
    is_active = models.BooleanField(_('Is active user'), default=True)
    is_admin = models.BooleanField(_('Administrator'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.last_name + ' ' + self.first_name

    full_name = property(get_full_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def __str__(self):
        return self.last_name + ' ' + self.first_name

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


def generate_email_hash():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(62))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', default='avatars/no-img.png')
    GENDER = (
        (1, _('male')),
        (2, _('female')),
    )

    gender = models.SmallIntegerField(_('Gender'), choices=GENDER, default=1)
    phone_number = models.CharField(_('Phone number'), max_length=20, null=True)
    birth_date = models.DateField(_('Birth date'), null=True)
    city = models.CharField(_('City'), max_length=100, null=True)
    is_verificated = models.BooleanField(_('Is user verificated'), default=False)
    verification_code = models.CharField(_('Verification code'), max_length=63, default=generate_email_hash)
    age_group = models.CharField(_('Age group'), max_length=63, default='')
    default_team = models.CharField(_('Default team name'), max_length=255, default='')

    ROLES = (
        (1, _('user')),
        (2, _('manager')),
    )
    role = models.SmallIntegerField(_('Role'), choices=ROLES, default=1)

    def update_data(self, **kwargs):
        self.gender = int(kwargs.get('gender', self.gender))
        self.phone_number = kwargs.get('phone_number', self.phone_number)
        if type(kwargs.get('birth_date', self.birth_date)) is not str:
            self.birth_date = kwargs.get('birth_date', self.birth_date)
        else:
            self.birth_date = datetime.datetime.strptime(kwargs['birth_date'], "%Y-%m-%d").date()

        age_group = self.get_age_group_numbers()
        if age_group:
            self.age_group = age_group
        self.city = kwargs.get('city', self.city)
        self.avatar = kwargs.get('avatar', self.avatar)
        self.default_team = kwargs.get('default_team', self.default_team)
        self.save()

    def get_age_group(self):
        try:
            born = self.birth_date
            today = datetime.date.today()
            age = today.year - born.year - 25
            if age < 0:
                return None
            groups = 'ABCDEFGHIJKLMN'
            age_group = groups[math.floor(age / 5)]
            return age_group
        except:
            return None

    def get_age_group_numbers(self):
        try:
            born = self.birth_date
            today = datetime.date.today()
            age = today.year - born.year - 25
            if age < 0:
                return None
            groups = ['25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94',]
            age_group = groups[math.floor(age / 5)]
            return age_group
        except:
            return None

    def get_age_group_number(self):
        try:
            born = self.birth_date
            today = datetime.date.today()
            age = today.year - born.year - 25
            if age < 0:
                return None
            return math.floor(age / 5)
        except:
            return None

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name

    def reset_code(self):
        self.verification_code = generate_email_hash()
        self.save()

    def get_default_team(self):
        if self.default_team:
            return self.default_team
        return str(_('Single'))


class ContactMessage(models.Model):
    full_name = models.CharField(_('Full name'), max_length=255, blank=True)
    email = models.CharField(_('Email'), max_length=255, blank=True)
    message = models.TextField(_('Message'))

    def __str__(self):
        return self.full_name + ' | ' + self.email
