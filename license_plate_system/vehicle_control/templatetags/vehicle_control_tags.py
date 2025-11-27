from django import template
from ..models import (
    RegisteredLicensePlate, VideoDetection,
    KnownLicensePlate, UnknownLicensePlate
)

register = template.Library()

@register.simple_tag
def get_registered_plates_count():
    return RegisteredLicensePlate.objects.count()

@register.simple_tag
def get_videos_count():
    return VideoDetection.objects.count()

@register.simple_tag
def get_known_detections_count():
    return KnownLicensePlate.objects.count()

@register.simple_tag
def get_unknown_detections_count():
    return UnknownLicensePlate.objects.count()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

