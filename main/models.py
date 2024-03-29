from django.db import models
from django.db.models import Subquery
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from .exceptions import CreateOrderError

import random
import string



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
    
    fund = models.FloatField(
        null = False,
        default = 0,
    )
    
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

class CurrenciesManager(models.Manager):
    
    def short_names_of_coins(self):
        """Вынимает уникальные 'currency_name_short' из ReceiveGiveCurrencies

        Returns:
            QuerySet: 'currency_name_short' из ReceiveGiveCurrencies
        """
        coins_to_give = self.get_queryset().values(
                                'give__currency_name_short'
                            ).exclude(
                                give__currency_name_short='RUB'
                            ).distinct()
        
        coins_to_receive = self.get_queryset().values(
                                'receive__currency_name_short'
                            ).exclude(
                                receive__currency_name_short='RUB'
                            ).distinct()
        
        short_names = coins_to_give.union(coins_to_receive)
        return short_names
    
class ReceiveGiveCurrencies(models.Model):
    
    objects = CurrenciesManager()
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

class OrderManager(models.Manager):

    def get_from_cache(self, random_string):

        """
            Возвращает один заказ из кэша

            return: Order
        """
        cache_key = 'Order.get_one_order(random_string={0})'.format(random_string)
        value = cache.get(cache_key)
        if not value:
            try:
                value = self.get_queryset().select_related(
                                'give',
                                'receive',
                                'give_token_standart',
                                'receive_token_standart',
                                'address_to',
                                'status',
                                'user').get(random_string=random_string)
                cache.set(cache_key, value, 1 * 60 * 60)
            except Exception as exception:
                raise exception
        return value
    
    def get_objects_from_cache(self, user, order_by):

        """ 
            Возвращает QuerySet заказов из кэша

            return QuerySet
        """
        
        return self.get_queryset().select_related(
                                        'give',
                                        'receive',
                                        'give_token_standart',
                                        'receive_token_standart',
                                        'address_to',
                                        'status',
                                    ).filter(user=user).order_by(*order_by)

    async def create_new_order(self, *args, **kwargs):

        """
            Создаёт новый заказ.

            number - номер заказа
            address - адрес, на который клиент переводит деньги
            random_string - случайная строка (slug), добавляемая к ссылке на обмен

            return: random_string
        """
        try:
            random_string = ''.join(random.choice(string.ascii_letters) for _ in range(200))

            await Order.objects.acreate(
                number=Subquery(Order.objects.order_by('-number').values('number')[:1]) + 1,
                random_string=random_string, 
                give_sum=kwargs['give_sum'], 
                receive_sum=kwargs['receive_sum'], 
                give_id=kwargs['give_payment_method_id'], 
                receive_id=kwargs['receive_payment_method_id'], 
                give_token_standart_id=kwargs['give_token_standart_id'], 
                receive_token_standart_id=kwargs['receive_token_standart_id'],
                receive_name='Без имени' if kwargs['receive_name'] == '' else kwargs['receive_name'],
                receive_address='Без адреса' if kwargs['receive_address'] == '' else kwargs['receive_address'],
                address_to_id=AddressTo.objects.filter(currency_id=kwargs['give_payment_method_id'],
                                                       token_standart=kwargs['give_token_standart_id']).values('id'),
                user=kwargs['user'],
                status_id=3,
            )

            return random_string
        except Exception as exception:
            raise CreateOrderError(**kwargs) from exception

    def update_status(self, random_string, confirm, *args, **kwargs):

        order = None
        try:
            order = self.get_queryset().filter(random_string=random_string)
        except:
            raise

        if confirm:
            order.update(status_id=2)
        else:
            order.delete()

        cache_key = 'Order.get_one_order(random_string={0})'.format(random_string)
        cache.delete(cache_key)
        
class Order(models.Model):
    
    """
        Заказ
    """
    
    objects = OrderManager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        indexes = [
            models.Index(fields=['random_string',]),
        ]
        
    number = models.IntegerField(
        null = False,
        default = 0,
        verbose_name = 'Номер заказа',
    )
    random_string = models.CharField(
        max_length = 200,
        null = False,
        default = 'Нет строки',
        verbose_name = 'Ссылка на заказ',
    )
    date_time = models.DateTimeField(
        null = False,
        default = timezone.now,
        verbose_name = 'Время и дата заказа',
    )
    give_sum = models.FloatField(
        null = False,
        default = 0,
        verbose_name = 'Cумма, которую отдаёт клиент',
    )
    receive_sum = models.FloatField(
        null = False,
        default = 0,
        verbose_name = 'Сумма, которую получает клиент',
    )
    give = models.ForeignKey(
        GiveCurrency,
        on_delete = models.SET_NULL,
        null = True,
        verbose_name = 'Валюта, которую отдаёт клиент',
    )
    receive = models.ForeignKey(
        ReceiveCurrency,
        on_delete = models.SET_NULL,
        null = True,
        verbose_name = 'Валюта, которую получает клиент',
    )
    give_token_standart = models.ForeignKey(
        TokenStandart,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'give_token_standart',
        verbose_name = 'Сеть криптовалюты, которую отдаёт клиент',
    )
    receive_token_standart = models.ForeignKey(
        TokenStandart,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'receive_token_standart',
        verbose_name = 'Сеть криптовалюты, которую получает клиент',
    )
    receive_name = models.CharField(
        max_length = 255,
        null = False,
        default = 'Без имени',
        verbose_name = 'Имя владельца карты',
    )
    receive_address = models.CharField(
        max_length = 255,
        null = False, 
        default = 'Без адреса',
        verbose_name = 'Адрес кошелька получателя',
    )
    address_to = models.ForeignKey(
        AddressTo,
        on_delete = models.SET_NULL,
        null = True,
        verbose_name = 'Адрес, на который клиент переводит свои деньги'
    )
    paid = models.BooleanField(
        null = False,
        default = False,
        verbose_name = 'Заказ исполнен'
    )
    user = models.ForeignKey(
        User,
        null = True,
        on_delete = models.SET_NULL,
        verbose_name = 'Клиент',
    )
    status = models.ForeignKey(
        OrderStatus,
        null = True,
        on_delete = models.SET_NULL,
        verbose_name = 'Статус заказа' 
    )

    def __str__(self) -> str:
        return f'Заказ {self.number}'
    
    def get_absolute_url(self):
        return reverse('order_info', kwargs={'random_string': self.random_string })

class FeedBackManager(models.Manager):

    def get_objects_from_cache(self):

        """
            Возвращает QuerySet отзывов из кэша

            return QuerySet
        """

        cache_key = 'feedback'
        value = cache.get(cache_key)
        if value == None:
            value = self.get_queryset().select_related('user').order_by('-date_time')[:20]
            cache.set(cache_key, value, 1 * 60 * 60)
        return value
    
class FeedBack(models.Model):
    """
        Отзыв клиента

        text - текст отзыва
        user - клиент
        date_time - дата и время создания отзыва
    """

    objects = FeedBackManager()
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
    display = models.BooleanField(
        null=False,
        default=False,
        verbose_name='Показывать',
    )