from django.urls import path, include
from . import views
from django.conf.urls.static import static
from cryptosite import settings



urlpatterns = [
    path('', views.ExchangeView.as_view(), name='main'),
    path('get_exchange_rate/', views.get_exchange_rate),
    path('rules/', views.rules, name='rules'),
    path('contacts/', views.contacts, name='contacts'),
    path('make_order/', views.ExchangeView.as_view()),
    path('start_exchange/exchange/confirm_payment/', views.OrderView.as_view()),
    path('orders/', views.OrdersList.as_view(), name='orders'),
    path('order/<slug:random_string>/', views.OrderView.as_view(), name='order_info'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)