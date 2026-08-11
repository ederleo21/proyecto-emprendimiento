"""Envoltorio uniforme de respuestas.

Espejo de `core_shared.my_response`. La forma `{status, message, data, errors}`
es la que ya esperan los frontends de InnoTech, así que se respeta al pie de la
letra aunque este servicio corra aparte.
"""
from rest_framework import status
from rest_framework.response import Response


class MyResponse:
    @staticmethod
    def success(data=None, message='Success', status_code=status.HTTP_200_OK):
        return Response({
            'status': 'success',
            'message': message,
            'data': data,
            'errors': None,
        }, status=status_code)

    @staticmethod
    def error(errors=None, message='Error', status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'status': 'error',
            'message': message,
            'data': None,
            'errors': errors,
        }, status=status_code)
