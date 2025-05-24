from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class CommonUtils():
    def __init__(self):
        pass
    def get_object(self, pk):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=pk)
    

class BaseAPIView(APIView):
    def _format_response(self, status_bool, message=None, data=None, status_code=status.HTTP_200_OK, pagination = None):
        response_data = {
            'status': status_bool,
            'message': message,
            'data': data
        }
        if pagination:
            response_data['total_pages'] = pagination.get('total_pages')
            response_data['total_items'] = pagination.get('count')
            response_data['current_page'] = pagination.get('number')

        return Response(response_data, status=status_code)