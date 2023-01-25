from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from cryptosite import settings

""" urlpatterns = [
    path('', views.index),
    path('start-exchange/', views.start_exchange),
    
    path('rules/', views.rules, name='rules'),
    path('get_exchange_rate/', views.get_exchange_rate),
    path('get_coins/', views.get_coins)
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) """

urlpatterns = [
    path('', views.index),
    path('get_exchange_rate/', views.get_exchange_rate),
    path('rules/', views.rules, name='rules'),
    path('select_coins/', views.select_coins),
    path('contacts/', views.contacts, name='contacts')
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)