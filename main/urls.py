from django.urls import path, include
from . import views
from django.conf.urls.static import static
from cryptosite import settings



urlpatterns = [
    path('', views.ExchangeView.as_view(), name='main'),
    path('get_exchange_rate/', views.get_exchange_rate),
    path('rules/', views.rules, name='rules'),
    path('contacts/', views.contacts, name='contacts'),
    path('start_exchange/', views.ExchangeView.as_view()),
    path('start_exchange/exchange/<str:random_string>', views.OrderView.as_view()),
    path('start_exchange/exchange/confirm_payment/', views.OrderView.as_view()),
    path('orders/', views.OrdersList.as_view(), name='orders'),
    path('orders/<str:random_string>/', views.OrderView.as_view(), name='order_info'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)