#!/usr/bin/venv python3
import uuid
import hashlib
from django.db import models
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

class UserManager(BaseUserManager):
    
    def create_user(self,email, password=None, **kwargs):
        if email is None:
            raise TypeError('Users must have an email.')
        if password is None:
            raise TypeError('User must have a password.')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email, password, **kwargs):
        if password is None:
            raise TypeError('Superusers must have a password.')
        if email is None:
            raise TypeError('Superusers must have an email.')

        user = self.create_user( email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    public_id = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)
    username = models.CharField(db_index=True, max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    confirm_password = models.CharField(max_length=1000, null=True, blank=True)
    profile_image=models.FileField(upload_to='photos',null=True,blank=True)
    is_company=models.BooleanField(default=False)
    is_student=models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        if self.confirm_password:
            self.confirm_password = hashlib.sha256(str(self.confirm_password).encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def name(self):
        return f"{self.full_name}"


class CompanyProfile(models.Model):
    company_phone_number=models.TextField(null=True,blank=True)
    company_name=models.TextField(null=True,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    company_url=models.TextField(null=True,blank=True)
    
class StudentProfile(models.Model):
    phone_number = models.CharField(max_length=1000, null=True, blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    student_id = models.CharField(max_length=20, null=True, blank=True)
    gender=models.CharField(max_length=20,null=True,blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)