import hashlib
import os

from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework.viewsets import ModelViewSet

from .base.models import User
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only list, create, retrieve,
    update, or delete their own bids.
    """
    model = User
    serializer_class = UserSerializer

    def get_object(self, qs=None):
        return self.request.user


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Home, self).get_context_data(**kwargs)
        ctx['gravatar_url'] = self.get_gravatar_url()
        return ctx

    def get_gravatar_url(self):
        email_hash = ''
        if self.request.user.is_authenticated():
            email_hash = hashlib.md5(self.request.user.email).hexdigest()
        return "http://www.gravatar.com/avatar/{}?s=40".format(
            email_hash)


def revision(request):
    return HttpResponse(os.environ.get('COMMIT_HASH', ''),
                        content_type='text/plain')
