from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create Managers Here
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self) \
            .get_queryset() \
            .filter(status='published')


class DraftedManager(models.Manager):
    def get_queryset(self):
        return super(DraftedManager, self).get_queryset().filter(status='draft')


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=250,
                            unique='name')
    description = models.TextField()

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING,
                                 related_name='blog_posts', null=True)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    objects = models.Manager()
    published = PublishedManager()
    drafted = DraftedManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title
