from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from . import exchangenetwork as network
from . import services
from cryptosite.settings import MEDIA_URL, NAV_BAR
from django.core.cache import cache
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from datetime import datetime
from django.contrib.auth import get_user
from .models import Order

import json
import logging



logging.getLogger('main')

class BaseContext(ContextMixin):

    extra_context = {
        'nav_bar': NAV_BAR,
        'MEDIA_URL': MEDIA_URL,
    }

class ExchangeView(View, BaseContext):
    
    template_name = 'main/coins.html'

    async def get(self, request, *args, **kwargs):

        """
            Главная страница сайта.

            return: HttpResponse
        """
        
        try:
            
            
            self.extra_context['title'] = 'Главная'
            self.extra_context['give_coins'] = [
                        coin for coin in await services.get_coins_to_give()
                ]
            
            self.extra_context['receive_coins'] = [
                        coin for coin in await services.get_coins_to_receive()
                ]
            
            self.extra_context['exchange_ways'] = json.dumps(
                list([coin for coin in await services.get_exchange_ways()]),
                )
            
            self.extra_context['give_tokens'] = json.dumps(
                list([coin for coin in await services.get_give_tokens()]),
                )
            
            self.extra_context['receive_tokens'] = json.dumps(
                list([coin for coin in await services.get_receive_tokens()]),
                )
            
            return render(
                request = request,
                template_name = self.template_name,
                context = self.get_context_data()
            )
        
        except Exception as exception:

            logging.exception(exception)

            return render(
                request = request,
                template_name = 'InternalError.html',
                status = 500,
                context = self.get_context_data()
            )
        
    async def post(self, request, *args, **kwargs):
        
        """
            Создаёт новый заказ.

            От клиента приходит ajax-запрос, который содержит данные заказа
            
            random_string - ссылка на заказ
            user - клиент, если он прошёл аутентификацию, иначе None

            return JsonResponse 
        """
        user = None
        if get_user(request).is_authenticated:
            user = get_user(request)

        random_string = await services.create_new_order(
            give_sum=request.POST['give_sum'],
            receive_sum=request.POST['receive_sum'],
            give_payment_method_id=request.POST['give_payment_method_id'],
            receive_payment_method_id=request.POST['receive_payment_method_id'],
            give_token_standart_id=request.POST['give_token_standart_id'],
            receive_token_standart_id=request.POST['receive_token_standart_id'],
            receive_name=request.POST['receive_name'],
            receive_address=request.POST['receive_address'],
            user=user
        )

        return JsonResponse(
            data={'link': 'start_exchange/exchange/{0}'.format(random_string)},
        )
    
def rules(request):

    if (request.method == 'GET'):
        context = {
            'nav_bar': NAV_BAR
        }
        return render(request, 'main/rules.html', context=context)

def contacts(request):

    pass

async def get_exchange_rate(request):
    
    try:
        rates = cache.get('rates')
        if not rates:

            exchange = network.ExchangeClient(
                network.CurrenciesFromMYSQL,
                network.CentreBankAPI
            )
            rates = await exchange.get_rate()

            cache.set('rates', rates, 1800)

        return JsonResponse(
            data={'rates': json.dumps(rates)},
            safe=False,
            json_dumps_params={'ensure_ascii': False},
        )
    except Exception as exception:
        logging.exception(exception)

class MakeOrderView(View, BaseContext):
    
    async def get(self, request, *args, **kwargs):
        """
            Находит заказ, считает сколько прошло времени с момента создания заказа.
            Клиент видит данные заказа и сколько времени осталось, чтобы оплатить его.

            return: HttpResponse
        """
        
        try:

            order = await services.get_order(kwargs['random_string'])
            self.extra_context['order'] = order

            delta = datetime.now() - order.date_time.replace(tzinfo=None)
            total_seconds = 1200 - delta.total_seconds()

            if (total_seconds <= 0):
                self.extra_context['minutes'] = '00'
                self.extra_context['seconds'] = '00'
            else:
                minutes = int(total_seconds / 60)
                seconds = int(((total_seconds / 60) % 1) * 60)
                self.extra_context['minutes'] = minutes if minutes >= 10 else '0{0}'.format(minutes)
                self.extra_context['seconds'] = seconds if seconds >= 10 else '0{0}'.format(seconds)
                
            return render(
                request = request,
                template_name = 'main/pay_order.html',
                context = self.get_context_data(),
            )
        
        except Exception as exception:

            logging.exception(exception)

            return render(
                request = request,
                template_name = 'InternalError.html',
                status = 500,
                context = self.get_context_data(),
            )

    async def post(self, request, *args, **kwargs):
        """
            Получает ответ от клиента о том, оплатил ли он заказ или нет.

            return: JsonResponse
        """

        try:
            order = await services.update_status(
                request.POST['random_string'],
                request.POST['confirm'],
            )

            return JsonResponse(
                data={ order.number, order.paid },
                safe=False,
                json_dumps_params={ 'ensure_ascii': False },
            )
        except Exception as exception:
            logging.exception(exception)

class OrdersList(ListView, BaseContext):
    
    template_name = 'main/order_list.html'
    ordering = ['-date_time',]
    context_object_name = 'orders'
    
    def get_context_data(self, **kwargs):
        self.extra_context['title'] = 'Заказы'
        return super().get_context_data(**kwargs)

    def get_queryset(self):

        if not get_user(self.request).is_authenticated:
            return

        return Order.objects.filter(user = get_user(self.request)).order_by(*self.get_ordering())
    
    def get(self, request, *args, **kwargs):

        if not get_user(request).is_authenticated:
            # TODO сделать сделать страницу access denied
            return 403
        
        return super().get(request, *args, **kwargs)

class OrderInfo(DetailView, BaseContext):

    model = Order
    template_name = 'main/order_info.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        self.extra_context['title'] = 'Заказ № {0}'.format(self.order.number)
        return super().get_context_data(**kwargs)
    
    def get_object(self, queryset = None):
        
        self.order = Order.objects.get(random_string = self.kwargs['random_string'])
        return self.order

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()

        if get_user(request) != self.object.user:
            # TODO сделать страницу access denied
            return 403
        
        context = self.get_context_data(object = self.object)
        return self.render_to_response(context)
