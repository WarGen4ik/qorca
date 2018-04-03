import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
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
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='First name',
        max_length=255
    )
    last_name = models.CharField(
        verbose_name='First name',
        max_length=255
    )
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField('Незаблокований користувач', default=True)
    is_admin = models.BooleanField('Адміністратор', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        # The user is identified by their email address
        return self.last_name + ' ' + self.first_name

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
        return self.email

    class Meta:
        verbose_name = 'Користувачі'
        verbose_name_plural = 'Користувачі'


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/no-img.png')
    GENDER = (
        (1, 'male'),
        (2, 'female'),
    )

    gender = models.SmallIntegerField(choices=GENDER, default=1)
    phone_number = models.CharField(max_length=20, null=True)
    birth_date = models.DateField(null=True)
    city = models.CharField(max_length=100, null=True)

    ROLES = (
        (1, 'user'),
        (2, 'manager'),
    )
    role = models.SmallIntegerField(choices=ROLES, default=1)

    def update_data(self, **kwargs):
        self.gender = int(kwargs.get('gender', self.gender))
        self.phone_number = kwargs.get('phone_number', self.phone_number)
        if type(kwargs.get('birth_date', self.birth_date)) is not str:
            self.birth_date = kwargs.get('birth_date', self.birth_date)
        else:
            self.birth_date = datetime.datetime.strptime(kwargs['birth_date'], "%Y-%m-%d").date()
        self.city = kwargs.get('city', self.city)
        self.avatar = kwargs.get('avatar', self.avatar)
        self.save()

    def __str__(self):
        return self.user.email
