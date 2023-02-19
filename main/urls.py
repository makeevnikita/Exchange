from django.urls import path
from . import views
from django.conf.urls.static import static
from cryptosite import settings

urlpatterns = [
    path('', views.ExchangeView.as_view()),
    path('get_exchange_rate/', views.get_exchange_rate),
    path('rules/', views.rules, name='rules'),
    path('contacts/', views.contacts, name='contacts'),
    path('test/', views.start_exchange, name='start_exchange')
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)