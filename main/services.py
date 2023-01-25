from main.models import ReceiveGiveCurrencies, TokenStandart
from django.core.cache import cache
from asgiref.sync import sync_to_async

@sync_to_async
def get_GiveCurrencies_from_database():

    giveCurrency = cache.get('giveCurrency')
    if not giveCurrency:
        try:
            giveCurrency = ReceiveGiveCurrencies.objects.select_related('receive',
                    'give').values('give_id',
                    'give__currency_name',
                    'give__currency_name_short',
                    'give__image',
                    'give__category_payment_method__id'
                    ).distinct()
            cache.set('giveCurrency', giveCurrency, 300)
            return giveCurrency
        except:
            pass
    else:
        return giveCurrency

@sync_to_async
def get_ReceiveGiveCurrencies():
    """
    Делает запрос в БД и возвращает данные из таблицы main_givecurrency
    """
    coins = cache.get('coins')
    if not coins:
        try:
            coins = ReceiveGiveCurrencies.objects.select_related(
                'receive',
                'give').values(
                'receive_id',
                'receive__currency_name',
                'receive__currency_name_short',
                'receive__image',
                'receive__token_standart__id',
                'receive__token_standart__token_standart',
                'receive__category_payment_method__id',
                'give_id',
                'give__currency_name',
                'give__currency_name_short',
                'give__image',
                'give__token_standart__id',
                'give__token_standart__token_standart',
                'give__token_standart__commission',
                'give__category_payment_method__id')
            cache.set('coins', coins, 300)
        except:
            pass
        
    return coins

@sync_to_async
def get_give_token_standart_commission_list():
    give_token_standart_commission = cache.get('give_token_standart_commission')
    if not give_token_standart_commission:
        try:
            give_token_standart_commission = TokenStandart.objects.values('token_standart',
                                                                          'commission').exclude(id=1).distinct()
            cache.set('give_token_standart_commission', give_token_standart_commission, 300)
            return give_token_standart_commission
        except:
            pass
    else:
        return give_token_standart_commission

@sync_to_async
def get_receive_token_standart_list():
    receive_token_standart = cache.get('receive_token_standart')
    if not receive_token_standart:
        try:
            receive_token_standart = ReceiveGiveCurrencies.objects.select_related('receive',
                    'give').values(
                    'receive_id',
                    'receive__token_standart__id',
                    'receive__token_standart__token_standart',
                    'receive__category_payment_method__id').exclude(receive__token_standart__id=1).distinct()
            cache.set('receive_token_standart', receive_token_standart, 300)
            return receive_token_standart
        except:
            pass
    else:
        return receive_token_standart