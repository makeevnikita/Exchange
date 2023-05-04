from main.models import Order, AddressTo, OrderStatus
from django.core.cache import cache
from .exceptions import *
from django.shortcuts import get_object_or_404

import logging



logging.getLogger('main')

async def update_status(random_string, confirm):

    order = None
    try:
        order = await get_object_or_404(Order, random_string = random_string)
    except Exception as exception:
        logging.exception(exception)
        raise
        # TODO обработать 
    if confirm:
        order.paid = confirm
        order.status = OrderStatus.objects.get(id = 2)
        order.save()
        return order
    else:
        order.delete()
