from distutils.command import upload
from tabnanny import verbose
from turtle import title
from unicodedata import category
from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.urls import reverse

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    avatar = models.ImageField(upload_to='user_images/')
    phone_number = models.CharField(max_length = 11)

class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)
        
class Category(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("store:category_list", args=[self.slug])

    def __str__(self):
        return self.title

class Product(models.Model):
    category = models.ForeignKey(Category, related_name = 'product', on_delete= models.CASCADE)
    created_by = models.ForeignKey(User, related_name = 'product_creator', on_delete = models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')
    description = models.TextField(blank= True)
    created = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    objects = models.Manager()
    products = ProductManager()
    
    # class Meta:
    #     ordering = ('-created',)
    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])
    
    def __str__(self):
        return self.title


    
