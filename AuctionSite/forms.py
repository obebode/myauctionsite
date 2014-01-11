
from auction import models
import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from auction.models import AuctionEvent, Bid


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email")


class confAuction(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)


class EditAuctionEventForm(ModelForm):
    class Meta:
        model = AuctionEvent
        exclude = ('Title', 'category', 'MinimumPrice', 'StartDate', 'EndDate','Seller', 'is_active','lockedby', 'winning_bidder' )


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model =  User
        fields = ('email',)


class AuctionEventForm(forms.ModelForm):
    class Meta:
        model = AuctionEvent
        exclude = ('is_active','status','is_banned','lockedby', 'winning_bidder')

        class Meta:
            ordering = ['StartDate']


    def clean_StartDate(self):
        cleaned_data = self.cleaned_data
        cleaned_StartDate = cleaned_data.get('StartDate')
        if cleaned_StartDate < datetime.datetime.now():
            raise ValidationError('Specified time occurs in the past.')
        return cleaned_StartDate

    def clean_EndDate(self):
        cleaned_data = self.cleaned_data
        cleaned_StartDate = cleaned_data.get('StartDate')
        cleaned_EndDate = cleaned_data.get('EndDate')
        if cleaned_EndDate < datetime.datetime.now() + datetime.timedelta(days=3) :
            raise ValidationError('Specified end date should be a minimum of 72hrs from the start date')
        return cleaned_EndDate

    def save(self, commit=True):
        auction_event = super(AuctionEventForm, self).save(commit=False)
        auction_event.save()
        return auction_event


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def __init__(self, data=None, auction_event=None, bidder=None, *args, **kwargs):
        self.auction_event = auction_event
        self.bidder = bidder
        super(BidForm, self).__init__(data, *args, **kwargs)


    def clean(self):
        cleaned_data = self.cleaned_data
        current_time = datetime.datetime.now()
        if current_time > self.auction_event.EndDate:
            raise ValidationError('This auction event has expired.')
        return cleaned_data


    def clean_amount(self):
        cleaned_data = self.cleaned_data
        cleaned_amount = cleaned_data.get('amount', Decimal('0.00'))

        if self.auction_event.bid_set.count():
            if cleaned_amount < self.auction_event.bid_set.order_by('-amount')[0].amount:
                raise ValidationError('Your bid should be higher than the current price.')
        return cleaned_amount

    def save(self, commit=True):
        bid = super(BidForm, self).save(commit=False)
        bid.auction_event = self.auction_event
        bid.bidder = self.bidder
        bid.save()
        self.auction_event.winning_bidder = bid.bidder
        self.auction_event.save()
        return bid


class AuctionSearchForm(forms.Form):
    query = forms.CharField(max_length=200, required=False, label='')

    def search(self):
        cleaned_data = self.cleaned_data
        cleaned_query =cleaned_data.get('query', '')
        found_auctions = AuctionEvent.objects.filter(Q(Title__icontains=cleaned_query))
        return found_auctions
