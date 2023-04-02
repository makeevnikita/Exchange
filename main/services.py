from main.models import ReceiveGiveCurrencies, Order, AddressTo
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db.models import Max
from .exceptions import *

import random
import string




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
            cache.set('give_coins', give_coins, 1800)
        except Exception as exception:
            raise GetCoinsToGiveException from exception
        
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
            cache.set('receive_coins', receive_coins, 1800)
        except Exception as exception:
            raise GetCoinsToReceiveException from exception
        
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
            cache.set('exchange_ways', exchange_ways, 1800)
        except Exception as exception:
            raise GetExchangeWaysException from exception
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
            cache.set('give_tokens', give_tokens, 1800)
        except Exception as exception:
            raise GetGiveTokensException from exception
        
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
            cache.set('receive_tokens', receive_tokens, 1800)
        except Exception as exception:
            raise GetReceiveTokensException from exception
        
    return receive_tokens

@sync_to_async
def get_short_names_of_coins():

    coins_name_short = cache.get('coins_name_short')
    
    if not coins_name_short:

        try:
            coins_name_short = []
            print(ReceiveGiveCurrencies.objects.all())
            for coin in ReceiveGiveCurrencies.objects\
                .values('give__currency_name_short', 'receive__currency_name_short')\
                .exclude(give__currency_name_short = 'RUB', receive__currency_name_short = 'RUB')\
                .distinct():
                
                if (coin['give__currency_name_short'] not in coins_name_short and coin['give__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['give__currency_name_short'])

                if (coin['receive__currency_name_short'] not in coins_name_short and coin['receive__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['receive__currency_name_short'])
                    
            cache.set('coins_name_short', coins_name_short, 1800)
        except Exception as exception:
            raise GetShortNamesOfCoinsException from exception
        
    return coins_name_short

async def create_new_order(**kwargs):

    """
        number - номер заказа
        address - адрес, на который клиент переводит деньги
        new_order - новый заказ
        random_string - случайная строка, добавляемая к ссылке на обмен 
    """
    try:
        number = await Order.objects.aaggregate(Max('number'))
        address = await ExchangeDBO.get_address(kwargs['receive_payment_method_id'], kwargs['give_token_standart_id'])
        random_string = ''.join(random.choice(string.ascii_letters) for i in range(200))
        
        new_order = Order(number=number['number__max'] + 1,
                        random_string=random_string, 
                        give_sum=kwargs['give_sum'], 
                        receive_sum=kwargs['receive_sum'], 
                        give_id=kwargs['give_payment_method_id'], 
                        receive_id=kwargs['receive_payment_method_id'], 
                        give_token_standart_id=kwargs['give_token_standart_id'], 
                        receive_token_standart_id=kwargs['receive_token_standart_id'],
                        receive_name='Без имени' if kwargs['receive_name'] == '' else kwargs['receive_name'],
                        receive_address='Без адреса' if kwargs['receive_address'] == '' else kwargs['receive_address'],
                        address_to_id=address.id)
        
        new_order.save()
        
        return random_string
    except Exception as exception:
        raise CreateOrderError(**kwargs) from exception

async def get_order(random_string):
    try:
        return await Order.objects.aget(random_string=random_string)
    except Exception as exception:
        raise GetOrderException(random_string) from exception

class ExchangeDBO:
     
    @classmethod
    async def get_address(cls, receive_address_id, token_standart_id):

        """
            Получаем все адреса для перевода денег. Храним их в кэше.
        """

        try:
            address_list = cache.aget('address_list')
            if address_list == None:
                address_list = AddressTo.objects.all()
                cache.set('address_list', address_list, 360)
                
            return address_list.get(currency_id = receive_address_id, token_standart_id = token_standart_id)
        except Exception as exception:
            raise GetAddressError(receive_address_id=receive_address_id, token_standart_id=token_standart_id) from exception