from django.shortcuts import render
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Main chat page view"""
    logger.info(f"Chat page accessed from IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'chat/chat.html')

def health_check(request):
    """Health check endpoint for load balancers"""
    return HttpResponse("OK", content_type="text/plain")