from rest_framework import status
from rest_framework.response import Response


def create_error_response(message):
    print("API ERROR: " + message)
    return Response({
        'status': status.HTTP_400_BAD_REQUEST,
        'message': message,
    }, status=status.HTTP_400_BAD_REQUEST)
