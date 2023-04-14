from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.cache import cache
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from datetime import datetime
from django.contrib.auth import get_user
from .models import Order
from . import exchangenetwork as network
from . import services
from cryptosite.settings import MEDIA_URL, NAV_BAR, IMAGES_URL

import json
import logging



logging.getLogger('main')

class Cache:

    cache_key = None


class ExchangeView(View, ContextMixin):
    
    """Главная страница сайта"""

    template_name = 'main/coins.html'
    extra_context = {
        'nav_bar': NAV_BAR,
        'MEDIA_URL': MEDIA_URL,
        'title': 'Главная',
    }

    async def get_objects(self):
        
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
        
    async def get_context_data(self, **kwargs):

        try:
            await self.get_objects()
        except Exception as exception:
            logging.exception(exception)
            
            self.template_name = '500.html'
            
        return super().get_context_data(**kwargs)

    async def get(self, request, *args, **kwargs):

        """
            Главная страница сайта.
            
            Здесь выполняются асинхронные запросы в базу данных
            Запросы вытягивают: валюту, которую может отдать клиент
                                валюту, которую может получить клиент
                                сети валют, в которых мы принимаем
                                сети валют, в которых мы отдаём
                                пути обмена (модель ManyToMany)

            return: HttpResponse
        """

        context = await self.get_context_data()
        return render(
                request = self.request,
                template_name = self.template_name,
                context = context,
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
            data={'link': 'order/{0}'.format(random_string)},
        )

def rules(request):

    if (request.method == 'GET'):
        context = {
            'nav_bar': NAV_BAR,
            'MEDIA_URL': MEDIA_URL,
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
 
class OrderView(DetailView):
    
    template_name = 'main/order_info.html'
    context_object_name = 'order'
    queryset = Order.objects.all()
    slug_field = 'random_string'
    slug_url_kwarg = 'random_string'

    extra_context = {
            'nav_bar': NAV_BAR,
            'MEDIA_URL': MEDIA_URL,
            'IMAGES_URL': IMAGES_URL,
        }
    
    def calculate_the_time(self, *args, **kwargs):

        """
            Считает сколько времени осталось на оплату

            return: dict
        """

        time = {}
        delta = datetime.now() - kwargs['date_time'].replace(tzinfo=None)
        total_seconds = 1200 - delta.total_seconds()
        if (total_seconds <= 0):
            time['minutes'] = '00'
            time['seconds'] = '00'
        else:
            minutes = int(total_seconds / 60)
            seconds = int(((total_seconds / 60) % 1) * 60)
            time['minutes'] = minutes if minutes >= 10 else '0{0}'.format(minutes)
            time['seconds'] = seconds if seconds >= 10 else '0{0}'.format(seconds)

        return time
    
    def get_context_data(self, **kwargs):
        
        self.object = kwargs['object']
        
        if self.object:

            if get_user(self.request) != self.object.user:
                raise PermissionDenied
            
            time = self.calculate_the_time(date_time = self.object.date_time)

            self.extra_context['title'] = 'Заказ №{0}'.format(self.object.number)

            self.extra_context['minutes'] = time['minutes']
            self.extra_context['seconds'] = time['seconds']

        return super().get_context_data(**kwargs)
    
    async def get(self, request, *args, **kwargs):

        """
            Находит заказ, считает сколько прошло времени с момента создания заказа.
            Клиент видит данные заказа и сколько времени осталось, чтобы оплатить его.
            
            return: HttpResponse
        """

        status_code = 200
        try:
            self.object = Order().get_one_order(
                random_string = kwargs['random_string'],)
        except ObjectDoesNotExist as exception:
            logging.exception(exception)
            self.template_name = '404.html'
            status_code = 404
        except PermissionDenied as exception:
            logging.exception(exception)
            status_code = 403
        except Exception as exception:
            logging.exception(exception)
            self.template_name = '500.html'
            status_code = 500
        
        return render(
                    request = request,
                    template_name = self.template_name,
                    context = self.get_context_data(object = getattr(self, 'object', None)),
                    status = status_code,
                )

    async def post(self, request, *args, **kwargs):
        """
            Получает ответ от клиента о том, оплатил ли он заказ или нет.

            return: JsonResponse
        """
        if request.POST['confirm']:
            order = await services.update_status(
                    kwargs['random_string'],
                    json.loads(request.POST.get('confirm')),
                )
            return JsonResponse(
                    data={ 'link': reverse('main') },
                    safe=False,
                    json_dumps_params={ 'ensure_ascii': False },
                )
        else:
            try:
                Order.objects.delete(random_string = kwargs['random_string'])
                return redirect('orders')
            except Exception as exception:
                logging.exception(exception)

class OrdersList(ListView):

    template_name = 'main/order_list.html'
    context_object_name = 'orders'
    extra_context = {
            'nav_bar': NAV_BAR,
            'MEDIA_URL': MEDIA_URL,
            'title': 'Заказы',
        } 
    ordering = ['-date_time',]

    def get_queryset(self):

        """
            Находит все заказы клиента, сортируя их по убыванию даты

            Если клиент анонимный, то возникает исключение PermissionDenied
        """

        if not get_user(self.request).is_authenticated:
            raise PermissionDenied
        
        return Order().get_objects(user = get_user(self.request)).order_by(*self.get_ordering())
    
    def get(self, request, *args, **kwargs):
        
        """
            Выводит спсиок заказов для зарегистрированного клиента.
            Если клиент анонимный, то переводит его на страницу login.
            
            return: HttpResponse
        """
        
        try:
            return super().get(request, *args, **kwargs)
        except PermissionDenied:
            return redirect(reverse('login'))
        except Exception as exception:
            logging.exception(exception)
            self.template_name = '500.html'
            # TODO
