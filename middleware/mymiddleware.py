import time 
from threading import local


thread_locals = local()

class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        thread_locals.path = request.path
        thread_locals.sql_count = 0
        thread_locals.sql_total = 0
        timestamp = time.monotonic()

        response = self.get_response(request)

        print(
           f'     Продолжительность запроса {request.path} - '
           f'{time.monotonic() - timestamp:.3f} сек. '
           f'Количество SQL-запросов {thread_locals.sql_count} '
           f'Продолжительность SQL-запросов {thread_locals.sql_total:.3f} '
        )

        thread_locals.sql_count = 0
        thread_locals.sql_total = 0
        thread_locals.path = ''

        return response