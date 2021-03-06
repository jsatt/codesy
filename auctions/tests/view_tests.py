from django.conf import settings
from django.test import TestCase
from model_mommy import mommy
import fudge
import rest_framework

from auctions import models, serializers, views


class BidViewSetTest(TestCase):
    def setUp(self):
        self.viewset = views.BidViewSet()

    def test_attrs(self):
        self.assertIsInstance(
            self.viewset, rest_framework.viewsets.ModelViewSet)
        self.assertEqual(self.viewset.model, models.Bid)
        self.assertEqual(
            self.viewset.serializer_class, serializers.BidSerializer)

    def test_pre_save(self):
        user = mommy.make(settings.AUTH_USER_MODEL)
        self.viewset.request = fudge.Fake().has_attr(user=user)
        obj = mommy.prepare('auctions.Bid')

        self.viewset.pre_save(obj)

        self.assertEqual(obj.user, user)

    def test_get_queryset(self):
        user1 = mommy.make('base.User')
        user2 = mommy.make('base.User')
        bid1 = mommy.make('auctions.Bid', user=user1)
        mommy.make('auctions.Bid', user=user2)
        mommy.make('auctions.Bid', user=user2)
        bid4 = mommy.make('auctions.Bid', user=user1)
        bid5 = mommy.make('auctions.Bid', user=user1)
        self.viewset.request = fudge.Fake().has_attr(user=user1)

        qs = self.viewset.get_queryset()

        self.assertSequenceEqual(qs.order_by('id'), [bid1, bid4, bid5])


class GetBidTest(TestCase):
    def setUp(self):
        self.view = views.GetBid()

    def test_attrs(self):
        self.assertIsInstance(self.view, rest_framework.views.APIView)
        self.assertEqual(
            self.view.renderer_classes,
            (rest_framework.renderers.TemplateHTMLRenderer,))

    @fudge.patch('auctions.views.Response')
    def test_get_existant_bid(self, mock_resp):
        user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'http://gh.com/project'
        bid = mommy.make('auctions.Bid', user=user, url=url)
        self.view.request = fudge.Fake().has_attr(
            user=user, QUERY_PARAMS={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': bid, 'url': url}, template_name='bid.html')

        self.view.get(self.view.request)

    @fudge.patch('auctions.views.Response')
    def test_get_nonexistant_bid_assigns_None(self, mock_resp):
        user = mommy.make(settings.AUTH_USER_MODEL)
        other_user = mommy.make(settings.AUTH_USER_MODEL)
        url = 'http://gh.com/project'
        mommy.make('auctions.Bid', user=other_user, url=url)
        self.view.request = fudge.Fake().has_attr(
            user=user, QUERY_PARAMS={'url': url})
        mock_resp.expects_call().with_args(
            {'bid': None, 'url': url}, template_name='bid.html')

        self.view.get(self.view.request)
