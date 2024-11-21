import base64

from django.conf import settings
from django.utils.timezone import activate
from django.utils.deprecation import MiddlewareMixin

from accounts.models import User


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_timezone = self.get_user_timezone(request.META.get('HTTP_AUTHORIZATION'))
        activate(user_timezone)

    def get_user_timezone(self, auth_header):
        try:
            _, auth_string = auth_header.split(' ')
            decoded_bytes = base64.b64decode(auth_string)
            decoded_string = decoded_bytes.decode('utf-8')
            username, _ = decoded_string.split(':')
            return User.objects.get(username=username).timezone
        except:
            return settings.TIME_ZONE
