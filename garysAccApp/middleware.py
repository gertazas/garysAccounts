from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class RoundNumbersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # print("Middleware executed!")  # Debugging line
        
        if isinstance(response, Response):  # Only process DRF responses
            response.data = self._round_numbers(response.data)
            # print("Modified response:", response.data)  # Debugging line
        return response

    def _round_numbers(self, data):
        if isinstance(data, dict):
            return {key: self._round_numbers(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._round_numbers(item) for item in data]
        elif isinstance(data, (int, float)):
            return round(data, 2)
        return data
