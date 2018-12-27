from django.contrib.auth import authenticate, login

class MobileClientLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
#       print(request.META['REMOTE_HOST'])

        if request.path.find('admin') == -1 and not request.user.is_authenticated():
            if request.GET.get('mobile', None) == 'authenticate':
                user = authenticate(username='mobile', password='mobile')
                if user and user.is_active:
                    login(request, user)

        return response
