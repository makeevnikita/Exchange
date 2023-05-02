from main.models import ReceiveGiveCurrencies, Order, AddressTo, OrderStatus
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db.models import Max
from .exceptions import *
from django.shortcuts import get_object_or_404

import random
import string
import logging



logging.getLogger('main')

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
def get_short_names_of_coins() -> list:

    """
        Вынимает короткие имена валют в формате:
        <QuerySet [
                    {'give__currency_name_short': str,
                    'receive__currency_name_short': str}]>.
        После этого вынимает оттуда уникальные значения и сохраняет их в list    

        return: coins_name_short
    """

    coins_name_short = cache.get('coins_name_short')
    
    if not coins_name_short:

        try:
            coins_name_short = []
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
        Создаёт новый заказ.

        number - номер заказа
        address - адрес, на который клиент переводит деньги
        new_order - новый заказ
        random_string - случайная строка, добавляемая к ссылке на обмен

        return: random_string
    """
    try:
        number = await Order.objects.aaggregate(Max('number'))
        address = get_address(
            kwargs['give_payment_method_id'],
            kwargs['give_token_standart_id'],
        )
        random_string = ''.join(random.choice(string.ascii_letters) for i in range(200))

        new_order = Order(
            number=number['number__max'] + 1,
            random_string=random_string, 
            give_sum=kwargs['give_sum'], 
            receive_sum=kwargs['receive_sum'], 
            give_id=kwargs['give_payment_method_id'], 
            receive_id=kwargs['receive_payment_method_id'], 
            give_token_standart_id=kwargs['give_token_standart_id'], 
            receive_token_standart_id=kwargs['receive_token_standart_id'],
            receive_name='Без имени' if kwargs['receive_name'] == '' else kwargs['receive_name'],
            receive_address='Без адреса' if kwargs['receive_address'] == '' else kwargs['receive_address'],
            address_to=address,
            user=kwargs['user'],
            status=OrderStatus.objects.get(id = 2),
        )
        
        new_order.save()
        
        return random_string
    except Exception as exception:
        raise CreateOrderError(**kwargs) from exception

async def get_order(random_string):
    try:
        return await Order.objects.aget(random_string=random_string)
    except Exception as exception:
        raise GetOrderException(random_string) from exception

async def update_status(random_string, confirm):

    order = None
    try:
        order = await get_object_or_404(Order, random_string = random_string)
    except Exception as exception:
        logging.exception(exception)
        raise
        # TODO обработать 
    print(f'\n\n{bool(confirm)} {confirm}\n\n')
    if confirm:
        order.paid = confirm
        order.status = OrderStatus.objects.get(id = 2)
        order.save()
        return order
    else:
        order.delete()

def get_address(give_address_id, token_standart_id):

    """
        Получаем адрес, на который клиент переводит свои деньги.
        Храним их в кэше.
        По мере необходимости вынимаем нужный адрес из кэша.

        return: адрес, на который клиент переводит свои деньги
        """

    try:
        address_list = cache.get('address_list')
        if address_list == None:
            address_list = AddressTo.objects.all()
            cache.set('address_list', address_list, 360)
            
        return address_list.get(currency_id = give_address_id,
                                token_standart_id = token_standart_id,
                            )
    except Exception as exception:
        raise GetAddressError(currency_id = give_address_id,
                              token_standart_id = token_standart_id,
                            ) from exception
    