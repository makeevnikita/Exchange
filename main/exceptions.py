class GetCoinsInfo(Exception):
    pass

class OrderError(Exception):
    pass

class AddressError(Exception):
    pass

class GetCoinsToGiveException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get coins to give')

class GetCoinsToReceiveException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get coins to receive')

class GetExchangeWaysException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get exchange ways')

class GetGiveTokensException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get give tokens')

class GetReceiveTokensException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get receive tokens')

class GetShortNamesOfCoinsException(GetCoinsInfo):

    def __init__(self) -> None:
        super().__init__('Failed to get short names of coins')

class GetOrderException(OrderError):

    def __init__(self, random_string) -> None:
        super().__init__(f'Failed to get order by random_string: {random_string}')

class CreateOrderError(OrderError):

    def __init__(self, **kwargs) -> None:
        super().__init__(f'Failed to create order with params {kwargs}')

class GetAddressError(AddressError):

    def __init__(self, **kwargs) -> None:
        super().__init__(f'Failed to get address by params {kwargs}')