from django.shortcuts import render

# REST Framework: https://www.django-rest-framework.org/
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HelloWorldView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {
            'message': 'Hello, World!'
        }

        return Response(content)

"""
Example Class-Based REST View:

class ExampleView(APIView):
    # if authentication is required
    permission_classes = (IsAuthenticated,)

    # for a get method
    def get(self, request):
        # initialize content dictionary
        content = {}

        # perform logic
        # to obtain parameters from GET request
        request.query_params['param_name']

        # return response
        return Response(content)

    # for a POST method
    def post(self, request):
        # initialize content dictionary
        content = {}

        # perform logic
        # to obtain parameters from POST request
        request.data['param_name']

        # return response
        return Response(content)
"""