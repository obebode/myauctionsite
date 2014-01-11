from auction.models import AUCTION_ITEM_STATUS_DISPUTED, AUCTION_ITEM_STATUS_EXPIRED

__author__ = 'obe'


def process_ended_auction(auction_event):
    bid_count = auction_event.bid_set.count()

    if bid_count:
        auction_event.status = AUCTION_ITEM_STATUS_DISPUTED
        auction_event.save()

    else:
        auction_event.status = AUCTION_ITEM_STATUS_EXPIRED
        auction_event.save()
