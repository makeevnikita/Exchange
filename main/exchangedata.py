from .models import FeedBack, ReceiveGiveCurrencies
from django.core.cache import cache

import json



class ExchangeData:

    def init_data(self):
        """Отправляет SQL-запросы

        Запросы вытягивают: валюту, которую может отдать клиент
                            валюту, которую может получить клиент
                            сети валют, в которых мы принимаем
                            сети валют, в которых мы отдаём
                            пути обмена (модель ManyToMany)
                            отзывы

        Returns:
            data (Dict[str, any]): Валюты для обмена, пути обмена, отзывы
        """

        data = {}

        give_coins = ReceiveGiveCurrencies.objects.values(
                                        'give_id',
                                        'give__currency_name',
                                        'give__currency_name_short',
                                        'give__image',
                                        'give__category_payment_method__id',).distinct()
        data['give_coins'] = list(give_coins)
        
        receive_coins = ReceiveGiveCurrencies.objects.values(
                                        'receive_id',
                                        'receive__currency_name',
                                        'receive__currency_name_short',
                                        'receive__image',
                                        'receive__category_payment_method__id',).distinct()
        data['receive_coins'] = list(receive_coins)
        
        exchange_ways = ReceiveGiveCurrencies.objects.values(
                                                            'give_id',
                                                            'receive_id',)
        data['exchange_ways'] = json.dumps(list(exchange_ways))
        
        give_tokens = ReceiveGiveCurrencies.objects.values(
                                                    'give_id',
                                                    'give__token_standart__id',
                                                    'give__token_standart__token_standart')\
                                                    .exclude(give__token_standart__id = 1).distinct()
        data['give_tokens'] = json.dumps(list(give_tokens))

        receive_tokens = ReceiveGiveCurrencies.objects.values(
                                                    'receive_id',
                                                    'receive__token_standart__id',
                                                    'receive__token_standart__token_standart')\
                                                    .exclude(receive__token_standart__id = 1).distinct()
        data['receive_tokens'] = json.dumps(list(receive_tokens))

        data['feedbacks'] = FeedBack.objects.select_related('user').order_by('-date_time')[:20]

        return data
        
    def get_data(self):
        a = 1 / 0
        cache_key = 'exchange_data'
        value = cache.get(cache_key)
        if value == None:
            value = self.init_data()
            cache.set(cache_key, value, 1 * 60 * 60)
        return value
