import time
import logging



class RequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        logging.getLogger('main')

    def __call__(self, request):
        
        timestamp = time.time()

        response = self.get_response(request)

        logging.info(f'Длительность запроса: {time.time() - timestamp:.3f} {request.path}')

        return response