import datetime

from rest_framework import status
from rest_framework.response import Response


def create_error_response(message):
    print("API ERROR: ")
    print(message)
    return Response({
        'status': status.HTTP_400_BAD_REQUEST,
        'message': message,
    }, status=status.HTTP_400_BAD_REQUEST)


def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False

    return True
