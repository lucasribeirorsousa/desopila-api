import json
import requests


class GatewayBase:
    """
    Gateway base class
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _request_api(self, route:str, method:str='GET', data:dict={}, headers:dict={}) -> dict:
        '''
        Request to Gateway API

        Args:
            route(str):     request route
            method(str):    request method
            data(dict):     request data
            headers(dict):     request headers

        Returns:
            response(dict): response from request
        '''
        http_method = ('POST', 'GET', 'PUT', 'PATCH', 'DELETE',)

        if not isinstance(route, str) or not isinstance(data, dict) or not isinstance(headers, dict) or method not in http_method:
            raise Exception('Request incorrect')

        url = f'{self._base_url}/{route}'
        
        response = requests.request(method=method, url=url, data=json.dumps(data), headers=headers,)
        
        return response

    def create_customer(self, *args, **kwargs):
        pass

    def create_card(self, *args, **kwargs):
        pass

    def delete_card(self, *args, **kwargs):
        pass

    def credit_card_payment(self, *args, **kwargs):
        pass
