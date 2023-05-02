from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth import get_user
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from datetime import datetime
from .models import Order, FeedBack, ReceiveCurrency, ReceiveGiveCurrencies
from .forms import FeedBackForm
from . import exchangenetwork as network
from . import services
from .exchangedata import ExchangeData
from cryptosite.settings import MEDIA_URL, NAV_BAR, IMAGES_URL

import json
import logging



logging.getLogger('main')

class ExchangeView(View, FormMixin, ContextMixin):
    
    """Главная страница сайта"""
    
    success_url = reverse_lazy('main')
    template_name = 'main/coins.html'
    extra_context = {
        'nav_bar': NAV_BAR,
        'MEDIA_URL': MEDIA_URL,
        'title': 'Главная',
    }
    form_class = FeedBackForm
    
    async def get_objects(self, *args, **kwargs):
        
        """
            Отправляет sql-запросы
            Запросы вытягивают: валюту, которую может отдать клиент
                                валюту, которую может получить клиент
                                сети валют, в которых мы принимаем
                                сети валют, в которых мы отдаём
                                пути обмена (модель ManyToMany)
                                отзывы
        """

        exchange_data = ExchangeData()
        self.extra_context['give_coins'] = exchange_data.get_data('give_coins')
        self.extra_context['receive_coins'] = exchange_data.get_data('receive_coins')
        self.extra_context['exchange_ways'] = exchange_data.get_data('exchange_ways')
        self.extra_context['give_tokens'] = exchange_data.get_data('give_tokens')
        self.extra_context['receive_tokens'] = exchange_data.get_data('receive_tokens')
        self.extra_context['feedbacks'] = exchange_data.get_data('feedbacks')

    async def get_context_data(self, *args, **kwargs):
        
        try:
            await self.get_objects()
        except Exception as exception:
            logging.exception(exception)
            
            self.template_name = '500.html'
            
        return super().get_context_data(**kwargs)

    async def get(self, request, *args, **kwargs):

        """
            Главная страница сайта.
            
            return: HttpResponse
        """
        
        try:
            context = await self.get_context_data()
        except Exception as exception:
            logging.exception(exception)
            
            self.template_name = '500.html'
        
        return render(
                request = self.request,
                template_name = self.template_name,
                context = context,
            )
        
    async def post(self, request, *args, **kwargs):
        
        """
            Принимает запросы:
                ajax-запрос на создание заказа
                запрос из формы на создание отзыва
        """
        if request.POST.get('give_sum'):
            return await self.create_order()
        elif request.POST.get('text'):
            return await self.create_feedback()

    async def create_order(self, *args, **kwargs):

        """
            Создаёт новый заказ.

            От клиента приходит ajax-запрос, который содержит данные заказа
            
            random_string - ссылка на заказ
            user - клиент, если он прошёл аутентификацию, иначе None

            return JsonResponse 
        """

        random_string = await services.create_new_order(
            give_sum=self.request.POST['give_sum'],
            receive_sum=self.request.POST['receive_sum'],
            give_payment_method_id=self.request.POST['give_payment_method_id'],
            receive_payment_method_id=self.request.POST['receive_payment_method_id'],
            give_token_standart_id=self.request.POST['give_token_standart_id'],
            receive_token_standart_id=self.request.POST['receive_token_standart_id'],
            receive_name=self.request.POST['receive_name'],
            receive_address=self.request.POST['receive_address'],
            user=get_user(self.request) if get_user(self.request).is_authenticated else None
        )

        return JsonResponse(
            data={'link': 'order/{0}'.format(random_string)},
        )
    
    async def create_feedback(self, *args, **kwargs):

        """
            Создаёт отзыв

            return: HttpResponse
        """

        form = self.get_form()
        if form.is_valid():
            await FeedBack.objects.acreate(
                    text=self.request.POST.get('text'),
                    user=get_user(self.request) if get_user(self.request).is_authenticated else None
                )
            return super().form_valid(form)

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
        
        if self.object:
            """
                Если создатель заказа это есть клиент
                или
                Если создатель заказа равен None и клиент анонимен
            """
            if (self.object.user == get_user(self.request)) or \
               (self.object.user == None and get_user(self.request).is_anonymous):
                time = self.calculate_the_time(date_time = self.object.date_time)

                self.extra_context['title'] = 'Заказ №{0}'.format(self.object.number)

                self.extra_context['minutes'] = time['minutes']
                self.extra_context['seconds'] = time['seconds']
            else:
                raise PermissionDenied

        return super().get_context_data(**kwargs)
    
    async def get(self, request, *args, **kwargs):

        """
            Находит заказ, считает сколько прошло времени с момента создания заказа.
            Клиент видит данные заказа и сколько времени осталось, чтобы оплатить его.
            
            return: HttpResponse
        """

        status_code = 200
        try:
            self.object = await Order().get_from_cache(
                    random_string = kwargs['random_string'],
                )
        except ObjectDoesNotExist as exception:
            logging.exception(exception)
            self.object = None
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

    async def get_queryset(self):

        """
            Находит все заказы клиента, сортируя их по убыванию даты

            Если клиент анонимный, то возникает исключение PermissionDenied
        """

        if not get_user(self.request).is_authenticated:
            raise PermissionDenied
        
        return await Order().get_objects_from_cache(user = get_user(self.request),
                                            order_by = self.get_ordering(),
                                        )
    
    async def get(self, request, *args, **kwargs):
        
        """
            Выводит список заказов для зарегистрированного клиента.
            Если клиент анонимный, то переводит его на страницу login.
            
            return: HttpResponse
        """
        
        try:
            self.object_list = await self.get_queryset()
            context = self.get_context_data()
            return self.render_to_response(context)
        except PermissionDenied:
            return redirect(reverse('login'))
        except Exception as exception:
            logging.exception(exception)
            self.template_name = '500.html'
            # TODO
