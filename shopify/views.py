from django.shortcuts import render
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')
