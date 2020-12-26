from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _



class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    stripe_customer = models.CharField(blank=True,default='',max_length=255)
    stripe_connect_account = models.CharField(blank=True,default='',max_length=255)
    sessions_available = models.ManyToManyField('management.Session',blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True,null=True)
    PANEL = 'PANEL'
    SPECTATOR = 'SPECTATE'
    ACCESS_CODE = 'ACCESS_CODE'
    SCOREBOARD = 'SCOREBOARD'
    PURCHASE_TYPE = [
        (PANEL,'Panel'),
        (SPECTATOR,'Spectate'),
        (ACCESS_CODE,'Access Code'),
        (SCOREBOARD,'Scoreboard'),
        ]
    type = models.CharField(max_length=2,choices=PURCHASE_TYPE,default=PANEL)
    session = models.ForeignKey('management.Session', on_delete=models.SET_NULL,default=None,null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2,default=0)
    quantity = models.IntegerField(default=1)
    stripe_payment = models.CharField(blank=True,default='',max_length=255)
    def total(self):
       return self.amount * self.quantity