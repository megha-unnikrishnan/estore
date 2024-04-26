from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=10, unique=True)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    wallet = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    otp_expiry_time = models.DateTimeField(null=True, blank=True)
    last_otp_regeneration = models.DateTimeField(null=True, blank=True)
    referral_code = models.CharField(default="ESTORE", null=True, blank=True, max_length=12)
    refered_by = models.CharField(max_length=250, null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Customuser'
        ordering=['id']

    def __str__(self):
        return '{}'.format(self.email)

class Forgotpassword(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    forgot_password_token=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

class UserAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)
    alt_mobile = models.CharField(max_length=10, blank=True)
    address = models.TextField()
    town = models.CharField(max_length=150)
    zipcode = models.IntegerField()
    nearby_location = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    created = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.name}"
# Create your models here.

class WalletBook(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.CharField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    increment = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)