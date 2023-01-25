from django.contrib import admin
from django import forms

from .models import *

@admin.register(TokenStandart)
class TokenStandartAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiveCurrency)
class ReceiveCurrencyAdmin(admin.ModelAdmin):
    pass

@admin.register(GiveCurrency)
class GiveCurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_name', 'currency_name_short')

@admin.register(ReceiveGiveCurrencies)
class ReceiveGiveCurrenciesAdmin(admin.ModelAdmin):
    list_display = ('get_give', 'get_receive', 'is_active')