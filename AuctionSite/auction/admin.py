from django.contrib import admin
from auction.models import  AuctionEvent,Seller,Bid




admin.site.register(AuctionEvent)
admin.site.register(Bid)
admin.site.register(Seller)