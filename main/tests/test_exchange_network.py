from django.test import TestCase, tag
from django.contrib.auth.models import User
from main import exchangenetwork as network
from main.models import ReceiveCurrency, GiveCurrency, ReceiveGiveCurrencies,\
                        TokenStandart, CategoryPaymentMethod
from main import services



class CoinsListTest(network.CurrenciesSource):
    """Класс с тестовыми данными.
       Наследуется от абстрактного класса CurrenciesSource 

    Returns:
        list: Захардкоженные названия валют
    """
    @classmethod
    def get_currency_list(cls):
        return ['ETH', 'BTC', 'TEST',]
    
class ExchangeNetworkTest(TestCase):
    
    """
        Проверяет возможность взять курсы валют из сторонних API
    """

    def setUp(cls):
        
        """
            user - пользователь
            tokens - сети криптовалют
            categories - способы оплаты
            receive_coins - валюты, которые может получить клиент
            give_coins - валюты, которые может отдать клиент
            receive_give_currencies - пути обмена (модель ManyToMany)
        """

        user = User.objects.create_user(username='user_test', password='QWEzxc1_')

        tokens = [
            {'token_standart': 'BIP20', 'commission': 0},
            {'token_standart': 'Нет сети', 'commission': 0},
            ]
        for token in tokens:
             TokenStandart.objects.create(**token)

        categories = [
            {'category_payment_method_name': 'Криптовалюта'},
            {'category_payment_method_name': 'Банк'},
            ]
        for category in categories:
            CategoryPaymentMethod.objects.create(**category)

        receive_coins = [
            {'currency_name': 'Bitcoin', 'currency_name_short': 'BTC', 'image': '', 
             'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
             'token_standart': (TokenStandart.objects.get(token_standart = 'BIP20'),)},
            {'currency_name': 'Etherium', 'currency_name_short': 'ETH', 'image': '', 
            'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
            'token_standart': (TokenStandart.objects.get(token_standart = 'BIP20'),)},
            {'currency_name': 'Сбербанк', 'currency_name_short': 'RUB', 'image': '', 
            'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Банк'),
            'token_standart': (TokenStandart.objects.get(token_standart = 'Нет сети'),)}
            ]
        
        for coin in receive_coins:

            receive_coin = ReceiveCurrency(
                                currency_name = coin['currency_name'],
                                currency_name_short = coin['currency_name_short'],
                                image = coin['image'],
                                category_payment_method = coin['category_payment_method'],
                            )
            receive_coin.save()
            receive_coin.token_standart.set(coin['token_standart'])
            receive_coin.save()
            
        give_coins = [
            {'currency_name': 'Сбербанк', 'currency_name_short': 'RUB', 'image': '', 
             'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Банк'),
             'token_standart': (TokenStandart.objects.get(token_standart = 'Нет сети'),)},
            ]
        
        for coin in give_coins:
            give_coin = GiveCurrency(
                                currency_name = coin['currency_name'],
                                currency_name_short = coin['currency_name_short'],
                                image = coin['image'],
                                category_payment_method = coin['category_payment_method'],
                            )
            give_coin.save()
            give_coin.token_standart.set(coin['token_standart'])
            give_coin.save()
            

        receive_give_currencies = ReceiveGiveCurrencies(
            receive = ReceiveCurrency.objects.get(currency_name = 'Bitcoin'),
            give = GiveCurrency.objects.get(currency_name = 'Сбербанк'),
        )
        receive_give_currencies.save()

        receive_give_currencies = ReceiveGiveCurrencies(
            receive = ReceiveCurrency.objects.get(currency_name = 'Etherium'),
            give = GiveCurrency.objects.get(currency_name = 'Сбербанк'),
        )
        receive_give_currencies.save()

    @tag('slow')
    async def test_rates_not_has_none(self):
        
        """
            Запрашивает курс валюты из стороннего API.
            Если хотя бы один курс равен None, то тест не пройден.
        """

        exchange = network.ExchangeClient(network.CurrenciesFromMYSQL, network.CentreBankAPI)
        rates = await exchange.get_rate()
        
        self.assertNotIn(None, rates.values())

    @tag('slow')
    async def test_rates_has_none(self):
        
        """
            Запрашивает курс валюты из стороннего API.
            Если хотя бы один курс равен None, то тест пройден.
        """

        exchange = network.ExchangeClient(CoinsListTest, network.CentreBankAPI)
        rates = await exchange.get_rate()
        
        self.assertIn(None, rates.values())
    
    @tag('fast')
    async def creating_orders(self):
            
        """
            Создаёт заказ.
        """

        random_string = await services.create_new_order(
            give_sum=1000,
            receive_sum=1000,
            give_payment_method_id=GiveCurrency.objects.get(currency_name_short='RUB').id,
            receive_payment_method_id=ReceiveCurrency.objects.get(currency_name_short='ETH').id,
            give_token_standart_id=TokenStandart.objects.get(token_standart='BIP20').id,
            receive_token_standart_id=TokenStandart.objects.get(token_standart='BIP20').id,
            receive_name='TEST_USER',
            receive_address='0000000000000000',
            user=User.objects.get(username='test_user')
        )
        self.assertTrue(random_string)