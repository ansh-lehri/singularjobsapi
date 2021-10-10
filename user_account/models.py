from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self,email,username,password=None):

        if not email:
            raise ValueError('Enter your mail address')

        if not username:
            raise ValueError('Enter your username')

        user = self.model(
            email = self.normailze_email(email),
            username = username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
    def create_superuser(self,email,username,password):

        if not email:
            raise ValueError('Enter your mail address')

        if not username:
            raise ValueError('Enter your username')

        user = self.create_user(
            email = self.normailze_email(email),
            password=password,
            username=username,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser):

    email               =   models.EmailField(verbose_name='email',max_length=100,editable=True,unique=True)
    username            =   models.CharField(verbose_name='username',max_length=20,unique=True)
    date_joined         =   models.DateTimeField(verbose_name='date joined',auto_now_add=True)
    last_login          =   models.DateTimeField(verbose_name='last login',auto_now=True)
    is_active           =   models.BooleanField(default=True)
    is_verified         =   models.BooleanField(default=False)
    is_staff            =   models.BooleanField(default=False)
    is_superuser        =   models.BooleanField(default=False)
    is_admin            =   models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,app_label):
        return True

class UserProfileModel(models.Model):
    
    email = models.EmailField(verbose_name='email',max_length=100,editable=True,unique=True)
    technical_skills = models.CharField(verbose_name='technical_skills',max_length=100)
    soft_skills = models.CharField(verbose_name='soft_skills',max_length=100,blank=True)
    job_types = models.CharField(verbose_name='job_types',max_length=100,blank=True)
    subject_interest = models.CharField(verbose_name='subject_interest',max_length=100,blank=True)
    linkedin_profile = models.URLField(verbose_name='linkedin_profile',blank=True)
    user_jobs_list_exist = models.BooleanField(editable=True)
    
    
    def save(self,*args,**kwargs):
        #super(UserProfileModel,self).save(force_insert,force_update,using,update_fields)
        super(UserProfileModel,self).save(*args,**kwargs)
    
    
    
    def __str__(self):
        return str(self.email)