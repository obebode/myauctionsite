from decimal import Decimal
from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import timedelta
import datetime


class Seller(models.Model):
    user = models.OneToOneField(User, related_name='seller')

    def __unicode__(self):
        return '%s' %self.user.username


AUCTION_ITEM_CATEGORY_CHOICES = (
    ('Electronics', 'Electronics'),
    ('Media', 'Media'),
    ('Clothing', 'Clothing'),
    ('General', 'General'),
    )

AUCTION_ITEM_STATUS_RUNNING = 1


AUCTION_ITEM_STATUS_EXPIRED = 2
AUCTION_ITEM_STATUS_DISPUTED = 3
AUCTION_ITEM_STATUS_BANNED = 4

AUCTION_ITEM_STATUS_CHOICES = (

    (AUCTION_ITEM_STATUS_RUNNING, 'Running'),
    (AUCTION_ITEM_STATUS_EXPIRED, 'Expired'),
    (AUCTION_ITEM_STATUS_DISPUTED, 'Disputed'),
    (AUCTION_ITEM_STATUS_BANNED, 'Banned'),
    )


class AuctionEventManager(models.Manager):
    def get_current_auctions(self):
        current_time = datetime.datetime.now()
        return self.filter(status=AUCTION_ITEM_STATUS_RUNNING, StartDate__lt=current_time, EndDate__gt=current_time)

class AuctionEvent(models.Model):

    Title = models.CharField(max_length=200)
    description = models.TextField(max_length=200)
    category = models.CharField(max_length=200,choices=AUCTION_ITEM_CATEGORY_CHOICES)
    MinimumPrice = models.DecimalField(max_digits=10, decimal_places=2)
    StartDate = models.DateTimeField(default=datetime.datetime.now())
    EndDate = models.DateTimeField()
    Seller = models.ForeignKey(User)
    winning_bidder = models.ForeignKey(User, related_name='won_auctions', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    status = models.IntegerField(choices=AUCTION_ITEM_STATUS_CHOICES, default=AUCTION_ITEM_STATUS_RUNNING)
    is_banned = models.BooleanField(default=False)
    objects = AuctionEventManager()
    lockedby = models.TextField(default="",blank=True)

    @classmethod
    def getByName(cls, Title):
        return cls.objects.get(Title=Title)

    @classmethod
    def exists(cls, Title):
        return len(cls.objects.filter(Title=Title)) > 0

    def __unicode__(self):
        return u'%s listed on %s' %(self.Title, self.StartDate)

    def has_started(self):
        return datetime.datetime.now() >= self.StartDate

    def has_ended(self):
        return datetime.datetime.now() >= self.EndDate

    def is_running(self):
        return self.has_started() and not self.has_ended() and self.status == AUCTION_ITEM_STATUS_RUNNING

    def get_status(self):
        return dict(AUCTION_ITEM_STATUS_CHOICES).get(self.status, 'N/A')

    def get_current_price(self):
        current_price = self.MinimumPrice
        bid_count = self.bid_set.count()

        if bid_count:
            highest_bid = self.bid_set.order_by('-amount')[0]
            current_price = highest_bid.amount
        return current_price

class Bid(models.Model):

    auction_event = models.ForeignKey(AuctionEvent)
    bidder = models.ForeignKey(User)
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2)

    def __unicode__(self):
        return u'Placed bid on %s by %s' % (self.auction_event.Title, self.bidder.username)





