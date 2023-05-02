from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver



class TokenStandart(models.Model):

    """
        Сеть криптовалюты
    """

    class Meta:
        verbose_name = 'Сеть криптовалюты'
        verbose_name_plural = 'Сети криптовалют'

    token_standart = models.CharField(max_length=10)
    commission = models.IntegerField(null=False, default=-1)
    
    def __str__(self) -> str:
        return self.token_standart

class CategoryPaymentMethod(models.Model):

    """
        Виды платёжных систем (банк, крипто, онлайн-кошелёк)
    """

    class Meta:
        verbose_name = 'Вид платёжной системы'
        verbose_name_plural = 'Виды платёжных систем'

    category_payment_method_name = models.CharField(
        max_length=255,
        null=False
    )

    def __str__(self) -> str:
        return self.category_payment_method_name

class AbstractCurrency(models.Model):

    """
        Абстрактный класс валют.

        currency_name - название платёжной системы   
        currency_name_short - название валюты кратко 
        image - логотип платёжной системы
        category_payment_method - категория платёжной системы (банк, крипто, онлайн-кошелёк)
        token_standart - сеть криптовалюты
    """

    class Meta:
        abstract = True

    currency_name = models.CharField(
        max_length = 150,
    )
    currency_name_short = models.CharField(
        max_length=10,
    )
    image = models.FileField(
        upload_to = 'images/coins/',
        null = False,
    )
    category_payment_method = models.ForeignKey(
        CategoryPaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
    )
    token_standart = models.ManyToManyField(
        TokenStandart,
    )

    def __str__(self) -> str:
        return f'{self.currency_name}'

class GiveCurrency(AbstractCurrency):

    """
        Валюты, которые отдаёт клиент
    """

    class Meta:
        verbose_name = 'Валюта, которую отдаёт клиент'
        verbose_name_plural = 'Валюты, которые отдаёт клиент'
    
class ReceiveCurrency(AbstractCurrency):

    """
        Валюты, которые отдаём мы
    """

    class Meta:
        verbose_name = 'Валюта, которую получает клиент'
        verbose_name_plural = 'Валюты, которые получает клиент'
    
class AddressTo(models.Model):
    
    """
        Наши кошельки, на которые клиенты переводят свои деньги.

        address - адрес, на который клиент переводит деньги
        currency - валюта которую отдаст клиент
        token_standart - сеть валюты
    """
    
    class Meta:
        verbose_name = 'Адрес для перевода'
        verbose_name_plural = 'Адреса для перевода'

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
        verbose_name = 'Путь обмена'
        verbose_name_plural = 'Пути обмена'

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
    
    @sync_to_async
    def get_coins_from_cache(self):

        cache_key = 'coins_for_exchange'
        value = cache.get(cache_key)
        if value == None:
            coins_to_give = ReceiveGiveCurrencies.objects.values(
                                    'give_id',
                                    'give__currency_name',
                                    'give__currency_name_short',
                                    'give__image',
                                    'give__category_payment_method__id',).distinct()
            coins_to_receive = ReceiveGiveCurrencies.objects.values(
                                    'receive_id',
                                    'receive__currency_name',
                                    'receive__currency_name_short',
                                    'receive__image',
                                    'receive__category_payment_method__id',).distinct()
            value = (
                [coin for coin in coins_to_give],
                [coin for coin in coins_to_receive],
            )
            cache.set(cache_key, value, 1 * 60 * 60)

        return value
    
    @sync_to_async
    def get_exchange_ways_from_cache(self):

        cache_key = 'exchange_ways'
        value = cache.get(cache_key)
        if value == None:
            value = ReceiveGiveCurrencies.objects.values(
                                                        'give_id',
                                                        'receive_id',)
            cache.set(cache_key, value, 1 * 30 * 60)
        return value
    
    @sync_to_async
    def get_tokens_from_cache(self):

        cache_key = 'tokens'
        value = cache.get(cache_key)
        if value == None:
            give_tokens = ReceiveGiveCurrencies.objects.values(
                                               'give_id',
                                               'give__token_standart__id',
                                               'give__token_standart__token_standart')\
                                                .exclude(give__token_standart__id = 1).distinct()
            receive_tokens = ReceiveGiveCurrencies.objects.values(
                                                'receive_id',
                                                'receive__token_standart__id',
                                                'receive__token_standart__token_standart')\
                                                .exclude(receive__token_standart__id = 1).distinct()
            value = (give_tokens, receive_tokens,)
            cache.set(cache_key, value, 1 * 30 * 60)
        return value
    
class OrderStatus(models.Model):

    class Meta:
        verbose_name = 'Статус заказы'
        verbose_name_plural = 'Статусы заказов'

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
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['random_string',]),
        ]
        
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
    
    async def get_from_cache(self, random_string):

        """
            Возвращает один заказ из кэша

            return: Order
        """

        cache_key = 'Order.get_one_order(random_string={0})'.format(self.random_string)
        value = cache.get(cache_key)
        if value == None:
            value = await Order.objects.select_related(
                                'give',
                                'receive',
                                'give_token_standart',
                                'receive_token_standart',
                                'address_to',
                                'status',
                                'user').aget(random_string=random_string)
            cache.set(cache_key, value, 1 * 60 * 60)
        return value
    
    async def get_objects_from_cache(self, user, order_by):

        """ TODO убрать
            Возвращает QuerySet заказов из кэша

            return QuerySet
        """

        cache_key = 'Orders.get_orders(user={0})'.format(user.username)
        value = cache.get(cache_key)
        if value == None:
            value = Order.objects.select_related(
                                'give',
                                'receive',
                                'give_token_standart',
                                'receive_token_standart',
                                'address_to',
                                'status').filter(user=user).order_by(*order_by)
        return value

class FeedBack(models.Model):
    """
        Отзыв клиента

        text - текст отзыва
        user - клиент
        date_time - дата и время создания отзыва
    """

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        
    text = models.TextField(
        null=False,
        default='Без отзыва',
        max_length=350,
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL
    )
    date_time = models.DateTimeField(
        null = False,
        default = timezone.now,
    )

    def get_objects_from_cache(self):

        """
            Возвращает QuerySet отзывов из кэша

            return QuerySet
        """

        cache_key = 'feedback'
        value = cache.get(cache_key)
        if value == None:
            value = FeedBack.objects.select_related('user').order_by('-date_time')[:20]
            cache.set(cache_key, value, 1 * 60 * 60)
        return value