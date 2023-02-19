from django.db import models
from django.shortcuts import reverse

class Article(models.Model):
    
    title = models.CharField(max_length=200, null=False, default='')
    slug = models.SlugField(max_length=255, null=False, default='', unique=True, verbose_name="URL")
    image = models.FileField(upload_to='images/news/', null=False, default='')
    text = models.TextField(null=False, default='')

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('article', kwargs={'article_slug': self.slug})