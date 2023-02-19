from django.shortcuts import render
from cryptosite.settings import MEDIA_URL
from django.core.cache import cache
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from news.models import Article
from asgiref.sync import sync_to_async

class Cache():

    async def get_queryset_cache_key(self):

        raise NotImplementedError
    
    async def get_queryset_from_cache(self, key):

        value = cache.get(key)
        if value:
            return value
        else:
            value = await self.get_queryset_data()
            cache.set(key, value)
            return value  

class ArticleListView(ListView, Cache):

    template_name = 'news/articles.html'
    object_list = 'articles'
    
    @sync_to_async
    def get_articles(self):

        return Article.objects.all()

    async def get_queryset_cache_key(self):

        return 'news'

    async def get_queryset_data(self):

        return await self.get_articles()

    async def get_queryset(self):

      key = await self.get_queryset_cache_key()
      value = await self.get_queryset_from_cache(key)
      return value
    
    async def get_context_data(self, **kwargs):

        kwargs['title'] = 'Новости'
        kwargs['MEDIA_URL'] = MEDIA_URL
        kwargs[self.object_list] = await self.get_queryset()
        return super().get_context_data(**kwargs)

    async def get(self, request, *args, **kwargs):

      context = await self.get_context_data()
      return render(request=request, template_name=self.template_name, context=context)

class ArticlePageView(DetailView, Cache):

    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    async def get_queryset_cache_key(self):

        return self.kwargs['article_slug']

    async def get_queryset_data(self):
        return await Article.objects.aget(slug=self.kwargs['article_slug'])

    async def get_object(self):

        key = await self.get_queryset_cache_key()
        value = await self.get_queryset_from_cache(key)
        return value

    async def get(self, request, *args, **kwargs):
        context = {}
        article = await self.get_object()
        context['title'] = article.title
        context[self.context_object_name] = article
        return render(request=request, template_name=self.template_name, context=context)