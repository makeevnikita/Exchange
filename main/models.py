from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from asgiref.sync import sync_to_async



class TokenStandart(models.Model):

    """
        Сеть криптовалюты
    """

    token_standart = models.CharField(max_length=10)
    commission = models.IntegerField(null=False, default=-1)
    
    def __str__(self) -> str:
        return self.token_standart

class CategoryPaymentMethod(models.Model):

    """
        Виды платёжных систем (банк, крипто, онлайн-кошелёк)
    """

    category_payment_method_name = models.CharField(
        max_length=255,
        null=False
    )

    def __str__(self) -> str:
        return self.category_payment_method_name

class GiveCurrency(models.Model):

    """
        Валюты, которые отдаёт клиент
        currency_name - название платёжно системы   
        currency_name_short - название валюты кратко 
        image - логотип платёжной системы
        category_payment_method - категория платёжной системы (банк, крипто, онлайн-кошелёк)
        token_standart - сеть криптовалюты
    """

    currency_name = models.CharField(
        max_length = 150,
    )
    currency_name_short = models.CharField(
        max_length = 10,
    )
    image = models.FileField(
        upload_to = 'images/coins/',
        null = False,
    )
    category_payment_method = models.ForeignKey(
        CategoryPaymentMethod,
        on_delete = models.SET_NULL,
        null = True,
    )
    token_standart = models.ManyToManyField(
        TokenStandart,
    )

    def __str__(self) -> str:
        return f'{self.currency_name}'

class ReceiveCurrency(models.Model):

    """
        Валюты, которые отдаём мы.

        currency_name - название платёжно системы   
        currency_name_short - название валюты кратко 
        image - логотип платёжной системы
        category_payment_method - категория платёжной системы (банк, крипто, онлайн-кошелёк)
        token_standart - сеть криптовалюты
        address - адрес, на который клиент переводит валюту
    """

    currency_name = models.CharField(max_length=150)
    currency_name_short = models.CharField(max_length=10)
    image = models.FileField(upload_to='images/coins/', null=False)
    category_payment_method = models.ForeignKey(CategoryPaymentMethod, on_delete=models.SET_NULL, null=True)
    token_standart = models.ManyToManyField(TokenStandart)

    def __str__(self) -> str:
        return f'{self.currency_name}'
    
class AddressTo(models.Model):
    
    """
        Наши кошельки, на которые клиенты переводят свои деньги.

        address - адрес, на который клиент переводит деньги
        currency - валюта которую отдаст клиент
        token_standart - сеть валюты
    """
    
    address = models.CharField(
        max_length = 255,
        null = False,
        default = 'Без адреса',
    )
    currency = models.ForeignKey(
        GiveCurrency,
        on_delete = models.SET_NULL,
        null = True,
    )
    token_standart = models.ForeignKey(
        TokenStandart,
        on_delete = models.SET_NULL,
        null = True,
    )

    def __str__(self) -> str:
        return f'{self.address}'

class ReceiveGiveCurrencies(models.Model):
    
    class Meta:
        unique_together = (('receive', 'give'),)

    receive = models.ForeignKey(
        ReceiveCurrency,
        on_delete = models.CASCADE,
        null = False,
    )
    give = models.ForeignKey(
        GiveCurrency,
        on_delete = models.CASCADE,
        null = False,
    )
    is_active = models.BooleanField(
        default = False,
        null = False,
    )

    def __str__(self) -> str:
        return f'{self.receive.currency_name} {self.give.currency_name}'
    def get_receive_currency_name(self):
        return self.receive.currency_name
    def get_give_currency_name(self):
        return self.give.currency_name

class OrderStatus(models.Model):

    status = models.CharField(
        max_length = 255,
        null = False,
        default = 'status',
    )

    def __str__(self) -> str:
        return self.status

class Order(models.Model):
    
    """
        Заказы.

        number - номер заказа
        random_string - ссылка на заказ
        date_time - время и дата заказа
        give_sum - сумма, которую отдаёт клиент
        receive_sum - сумма, которую получает клиент
        give - валюта, которую отдаёт клиент
        receive - валюта, которую получает клиент
        give_token_standart - сеть криптовалюты, которую отдаёт клиент
        receive_token_standart - сеть криптовалюты, которую получает клиент
        receive_name - имя получателя
        receive_address - адрес кошелька получателя
        address_to - адрес, на который клиент переводит свои деньги
        paid - исполнен ли заказ
        user - заказчик
        status - статус заказа
    """
    
    number = models.IntegerField(
        null = False,
        default = 0,
    )
    random_string = models.CharField(
        max_length = 200,
        null = False,
        default = 'Нет строки',
    )
    date_time = models.DateTimeField(
        null = False,
        default = timezone.now,
    )
    give_sum = models.FloatField(
        null = False,
        default = 0,
    )
    receive_sum = models.FloatField(
        null = False,
        default = 0,
    )
    give = models.ForeignKey(
        GiveCurrency,
        on_delete = models.SET_NULL,
        null = True,
    )
    receive = models.ForeignKey(
        ReceiveCurrency,
        on_delete = models.SET_NULL,
        null = True,
    )
    give_token_standart = models.ForeignKey(
        TokenStandart,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'give_token_standart',
    )
    receive_token_standart = models.ForeignKey(
        TokenStandart,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'receive_token_standart',
    )
    receive_name = models.CharField(
        max_length = 255,
        null = False,
        default = 'Без имени',
    )
    receive_address = models.CharField(
        max_length = 255,
        null = False, 
        default = 'Без адреса',
    )
    address_to = models.ForeignKey(
        AddressTo,
        on_delete = models.SET_NULL,
        null = True,
    )
    paid = models.BooleanField(
        null = False,
        default = False,
    )
    user = models.ForeignKey(
        User,
        null = True,
        on_delete = models.SET_NULL,
    )
    status = models.ForeignKey(
        OrderStatus,
        null = True,
        on_delete = models.SET_NULL,
    )

    def __str__(self) -> str:
        return f'Заказ {self.number}'
    
    def get_absolute_url(self):
        return reverse('order_info', kwargs={'random_string': self.random_string })
    
    async def get_one_order(self, random_string):

        """
            Возвращает один заказ из кэша

            return: Order
        """

        cache_key = 'Order.get_one_order(random_string={0})'.format(self.random_string)
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return cache_value
        order = await Order.objects.select_related(
                                'give',
                                'receive',
                                'give_token_standart',
                                'receive_token_standart',
                                'address_to',
                                'status').aget(random_string=random_string)
        cache.set(cache_key, cache_value, 1 * 60 * 60)
        return order
    
    async def get_objects(self, user, order_by):

        """
            Возвращает список заказов из кэша

            return QuerySet
        """

        cache_key = 'Orders.get_orders(user={0})'.format(user.username)
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return cache_value
        order = Order.objects.select_related(
                                'give',
                                'receive',
                                'give_token_standart',
                                'receive_token_standart',
                                'address_to',
                                'status').filter(user=user).order_by(*order_by)
        cache.set(cache_key, cache_value, 1 * 60 * 60)
        return order
