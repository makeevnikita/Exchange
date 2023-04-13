from django.test import TransactionTestCase, tag
from main.models import ReceiveCurrency, GiveCurrency, ReceiveGiveCurrencies,\
                        TokenStandart, CategoryPaymentMethod, Order, AddressTo
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import login, logout



class UrlTest(TransactionTestCase):

    """
        Тестирует ссылки
    """

    def setUp(self):
        
        """
            user - пользователь
            tokens - сети криптовалют
            categories - способы оплаты
            receive_coins - валюты, которые может получить клиент
            give_coins - валюты, которые может отдать клиент
            receive_give_currencies - пути обмена (модель ManyToMany)
            addresses - адреса, на которые клиент переводит деньги
        """

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

        addresses = [
            {'address': 'address_test_1',
             'currency': GiveCurrency.objects.get(currency_name = 'Сбербанк'),
             'token_standart': TokenStandart.objects.get(token_standart = 'Нет сети')},
        ]

        for address in addresses:
            AddressTo.objects.create(**address)

    @tag('fast')
    def test_main_page(self):
        
        """
            Проверяет работоспособность главной страницы
        """

        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/coins.html')
    
    @tag('fast')
    def test_get_order_info(self):
        
        """
            Пользователь имеет доступ к своему заказу
            
            Создаёт пользователя user и логинит его
            Создаёт заказ, в котором user является заказчиком
            user пытается получить доступ к своему заказу

            Причина по которой тест не пройден: 
                Ответ сервера не содержит шаблон "main/order_info.html"
                Код ответа не равен 200
        """

        credentials = { 'username': 'user_test', 'password': 'QWEzxc1_'}
        user = User.objects.create_user(credentials)
        self.client.force_login(user)

        Order.objects.create(
            number=1,
            random_string='random_string', 
            give_sum=100, 
            receive_sum=100, 
            give_id=GiveCurrency.objects.get(currency_name = 'Сбербанк').id,
            receive_id=ReceiveCurrency.objects.get(currency_name = 'Etherium').id, 
            give_token_standart_id=TokenStandart.objects.get(token_standart = 'Нет сети').id,
            receive_token_standart_id=TokenStandart.objects.get(token_standart = 'BIP20').id,
            receive_name='Без имени',
            receive_address='Без адреса',
            address_to_id=AddressTo.objects.get(currency__currency_name = 'Сбербанк').id,
            user=user,
        )

        response = self.client.get(reverse('order_info', args=['random_string',]))
        self.assertTemplateUsed(response, 'main/order_info.html')
        self.assertEqual(response.status_code, 200)

    @tag('fast')
    def test_user_dont_have_access_to_order_info(self):
        
        """
            Пользователь не имеет доступа к чужому заказу
            
            Создаёт пользователя user
            Создаёт заказ, в котором user является заказчиком
            Аноним пытается получить доступ к созданному заказу

            Причина по которой тест не пройден: 
                Ответ сервера не содержит шаблон "403.html"
                Код состояния не равен 403
        """

        credentials = { 'username': 'user_test', 'password': 'QWEzxc1_'}
        user = User.objects.create_user(credentials)

        Order.objects.create(
            number=1,
            random_string='random_string', 
            give_sum=100, 
            receive_sum=100, 
            give_id=GiveCurrency.objects.get(currency_name = 'Сбербанк').id,
            receive_id=ReceiveCurrency.objects.get(currency_name = 'Etherium').id, 
            give_token_standart_id=TokenStandart.objects.get(token_standart = 'Нет сети').id,
            receive_token_standart_id=TokenStandart.objects.get(token_standart = 'BIP20').id,
            receive_name='Без имени',
            receive_address='Без адреса',
            address_to_id=AddressTo.objects.get(currency__currency_name = 'Сбербанк').id,
            user=user,
        )

        response = self.client.get(reverse('order_info', args=['random_string',]))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

    @tag('fast')
    def test_get_orders(self):

        """
            Аноним не имеет доступа списку заказов 
            и его переводит на страницу логина
            
            Создаёт пользователя user
            Создаёт заказ, в котором user является заказчиком

            Причина по которой тест не пройден:
                Код ответа не равен 403
                Ответ сервера не содержит шаблон "main/orders.html"
        """

        credentials = { 'username': 'user_test', 'password': 'QWEzxc1_'}
        user = User.objects.create_user(credentials)

        Order.objects.create(
            number=1,
            random_string='random_string', 
            give_sum=100, 
            receive_sum=100, 
            give_id=GiveCurrency.objects.get(currency_name = 'Сбербанк').id,
            receive_id=ReceiveCurrency.objects.get(currency_name = 'Etherium').id, 
            give_token_standart_id=TokenStandart.objects.get(token_standart = 'Нет сети').id,
            receive_token_standart_id=TokenStandart.objects.get(token_standart = 'BIP20').id,
            receive_name='Без имени',
            receive_address='Без адреса',
            address_to_id=AddressTo.objects.get(currency__currency_name = 'Сбербанк').id,
            user=user,
        )

        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 302)
