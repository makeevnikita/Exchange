from main.models import ReceiveGiveCurrencies, Order, ReceiveAddress
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db.models import Max

from .exceptions import *

import random
import string
import httpx



@sync_to_async
def get_coins_to_give():
    """
        Получить монеты, которые может отдать клиент
    """
    give_coins = cache.get('give_coins')
    if not give_coins:
        try:
            give_coins = ReceiveGiveCurrencies.objects.values(
                                    'give_id',
                                    'give__currency_name',
                                    'give__currency_name_short',
                                    'give__image',
                                    'give__category_payment_method__id').distinct()
        except:
            raise GetCoinsToGiveException
    return give_coins

@sync_to_async
def get_coins_to_receive():
    """
        Получить монеты, которые может получить клиент
    """
    receive_coins = cache.get('receive_coins')
    if not receive_coins:
        try:
            receive_coins = ReceiveGiveCurrencies.objects.values(
                                                'receive_id',
                                                'receive__currency_name',
                                                'receive__currency_name_short',
                                                'receive__image',
                                                'receive__category_payment_method__id').distinct()
        except:
            raise GetCoinsToReceiveException
    return receive_coins

@sync_to_async
def get_exchange_ways():
    """
        Получить пути обмена
    """

    exchange_ways = cache.get('exchange_ways')
    if not exchange_ways:
        try:
            exchange_ways = ReceiveGiveCurrencies.objects.values(
                                        'give_id',
                                        'receive_id')
        except:
            raise GetExchangeWaysException
    return exchange_ways

@sync_to_async
def get_give_tokens():

    give_tokens = cache.get('give_tokens')
    if not give_tokens:
        try:
            give_tokens = ReceiveGiveCurrencies.objects.values('give_id',
                                               'give__token_standart__id',
                                               'give__token_standart__token_standart')\
                                                .exclude(give__token_standart__id = 1).distinct()
        except:
            raise GetGiveTokensException
    return give_tokens

@sync_to_async
def get_receive_tokens():

    receive_tokens = cache.get('receive_tokens')
    if not receive_tokens:
        try:
            receive_tokens = ReceiveGiveCurrencies.objects.values('receive_id',
                                                'receive__token_standart__id',
                                                'receive__token_standart__token_standart')\
                                                .exclude(receive__token_standart__id = 1).distinct()
        except:
            raise GetReceiveTokensException
    return receive_tokens

@sync_to_async
def get_short_names_of_coins():

    coins_name_short = cache.get('coins_name_short')
    if not coins_name_short:
        try:
            coins_name_short = []
            for coin in ReceiveGiveCurrencies.objects.values('give__currency_name_short','receive__currency_name_short')\
                                                .exclude(give__currency_name_short='RUB',receive__currency_name_short='RUB')\
                                                .distinct():
                
                if (coin['give__currency_name_short'] not in coins_name_short and coin['give__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['give__currency_name_short'])
                if (coin['receive__currency_name_short'] not in coins_name_short and coin['receive__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['receive__currency_name_short'])
        except:
            raise GetShortNamesOfCoinsException
    return coins_name_short

async def create_new_order(**kwargs):
    """
        number - номер заказа
        address - адрес, на который клиент переводит деньги
        new_order - новый заказ
        random_string - случайная строка, добавляемая к ссылке на обмен 
    """
    number = await Order.objects.aaggregate(Max('number'))
    address = await ExchangeDBO.get_address(kwargs['receive_payment_method_id'])
    random_string = ''.join(random.choice(string.ascii_letters) for i in range(200))
    
    new_order = Order(number=number['number__max'] + 1,
                      random_string=random_string, 
                      give_sum=kwargs['give_sum'], 
                      receive_sum=kwargs['receive_sum'], 
                      give_id=kwargs['give_payment_method_id'], 
                      receive_id=kwargs['receive_payment_method_id'], 
                      give_token_standart_id=kwargs['give_token_standart_id'], 
                      receive_token_standart_id=kwargs['receive_token_standart_id'],
                      give_name=kwargs['give_name'],
                      give_address=kwargs['give_address'],
                      receive_address_id=address.id)
    
    new_order.save()
    
    return random_string

async def get_order(random_string):
    try:
        return await Order.objects.aget(random_string=random_string)
    except:
        raise GetOrderException(random_string)

class ExchangeDBO:
     
    @classmethod
    async def get_address(cls, receive_address_id):
        """
            Получаем все адреса для перевода денег. Храним их в кэше.
        """
        address_list = cache.get('address_list')
        if address_list == None:
            address_list = ReceiveAddress.objects.all()
            cache.set('address_list', address_list, 360)
            
        return address_list.get(currency_id = receive_address_id)

class NetworkAPI:

    @classmethod
    async def get_rate(cls, currency_name):
        raise NotImplementedError

class PoloniexAPI:
    SPECIFIC_RATE = 'https://api.poloniex.com/markets/{}/markPrice'

    @classmethod
    async def get_rate(cls, currency_name):
        try:
            pair = currency_name + '_USDT'
            print(cls.SPECIFIC_RATE.format(pair))
            async with httpx.AsyncClient() as client:
                response = await client.get(cls.SPECIFIC_RATE.format(pair))
            if (response.status_code != 200):
                raise ConnectionError
            return response.json()["markPrice"]
        except:
            raise ConnectionError

class BitpayAPI:
    SPECIFIC_RATE = 'https://bitpay.com/rates/{}/usd'

    @classmethod
    async def get_rate(cls, currency):
        try:
            print(cls.SPECIFIC_RATE.format(currency))
            async with httpx.AsyncClient() as client:
                    response = await client.get(cls.SPECIFIC_RATE.format(currency))
            if (response.status_code != 200):
                    raise ConnectionError
            return response.json()['data']['rate']
        except:
            raise ConnectionError
            
class ExchangeService:
    SPECIFIC_RATES = [PoloniexAPI.get_rate, BitpayAPI.get_rate]
                
    @classmethod
    async def get_rate_crypto(cls):
        rate_dict = {}
        coins = [coin for coin in await get_short_names_of_coins()]
        for coin in coins:
            for api in cls.SPECIFIC_RATES:
                try:
                    rate = await api(coin)
                    if (rate != None):
                        rate_dict[coin] = float(rate)
                        break
                except:
                    pass
        return rate_dict
        
    async def get_usdt_rate():
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
            if (response.status_code != 200):
                    raise ConnectionError
            return response.json()['Valute']['USD']['Value']
        except:
            pass