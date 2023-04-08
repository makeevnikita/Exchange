from django.test import TestCase
from django.contrib.auth.models import User
from main import exchangenetwork as network
from main.models import ReceiveCurrency, GiveCurrency, ReceiveGiveCurrencies,\
                        TokenStandart, CategoryPaymentMethod
from main import services


class CoinsListTest(network.CurrenciesSource):

    @classmethod
    async def get_currency_list(cls):
        return ['ETH', 'BTC', 'TEST',]
    
class ExchangeViewTest(TestCase):

    def test_exchange_view(self):

        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

class ExchangeNetworkTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        
        User.objects.create_user(username='user_test', password='QWEzxc1_')

        tokens = ['BIP20', 'Нет сети']
        for token in tokens:
            token_standart = TokenStandart(token_standart = token,
                                           commission = 0,
                                        )
            token_standart.save()

        categories = ['Криптовалюта', 'Банк']
        for category in categories:
            category_payment_method = CategoryPaymentMethod(category_payment_method_name = category)
            category_payment_method.save()

        receive_coins = [
            {'currency_name': 'Bitcoin', 'currency_name_short': 'BTC', 'image': '', 
             'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
             'token_standart': [TokenStandart.objects.get(token_standart = 'BIP20')]},
            {'currency_name': 'Etherium', 'currency_name_short': 'ETH', 'image': '', 
            'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
            'token_standart': [TokenStandart.objects.get(token_standart = 'BIP20')]},
            {'currency_name': 'Сбербанк', 'currency_name_short': 'RUB', 'image': '', 
            'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Банк'),
            'token_standart': [TokenStandart.objects.get(token_standart = 'Нет сети')]}
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
             'token_standart': [TokenStandart.objects.get(token_standart = 'Нет сети')]},
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

        
    async def test_rates_not_has_none(self):
        
        """
            Запрашивает курс валюты из стороннего API.
            Если курс равен None, то тест не пройдёт.
        """

        exchange = network.ExchangeClient(network.CurrenciesFromMYSQL, network.CentreBankAPI)
        rates = await exchange.get_rate()
        print('Rates:{0}'.format(rates.items()))
        
        self.assertTrue(None not in rates.values())

    async def test_rates_has_none(self):
        
        """
            Запрашивает курс валюты из стороннего API.
            Если курс равен None, то тест пройдёт.
        """

        exchange = network.ExchangeClient(CoinsListTest, network.CentreBankAPI)
        rates = await exchange.get_rate()
        print('Rates:{0}'.format(rates.items()))
        
        self.assertTrue(None in rates.values())
        
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