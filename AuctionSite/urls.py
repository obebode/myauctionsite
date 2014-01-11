
import django
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls import *
from auction.views import *
from django.views.decorators.csrf import csrf_exempt
from YaaasApp.auction import views as YaaasApp_views


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YaaasApp.views.home', name='home'),
    # url(r'^YaaasApp/', include('YaaasApp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^createuser/$', 'YaaasApp.auction.views.register'),
    url(r'^password_change/$', 'YaaasApp.auction.views.password_change'),
    url(r'^edituser/$', 'YaaasApp.auction.views.edituser'),
    #(r'^auction/$', 'YaaasApp.auction.views.index'),
    url(r'^home/$', YaaasApp_views.view_user_home, name='Yaas_user_home'),
    url(r'^index/$', YaaasApp_views.index, name='YaaasApp_index'),

    (r'^login/$', 'YaaasApp.auction.views.login_view'),
    (r'^logout/$', 'YaaasApp.auction.views.logout'),

    (r'^createauctionConf/$', 'YaaasApp.auction.views.createauctionConf'),
    (r'^saveauctionConf/$', 'YaaasApp.auction.views.saveauctionConf'),

    (r'^create_auction_event/$', 'YaaasApp.auction.views.create_auction_event'),
    (r'^edit_description/(?P<id>\d+)/$', 'YaaasApp.auction.views.edit_description'),


    (r'^api/v1/search/(\d{1,3})$', apisearch),
    (r'^auctions/$', 'YaaasApp.auction.views.auction_list'),

    (r'^change_Email/$', 'YaaasApp.auction.views.ChangeEmail'),


    url(r'^view_auction_event/(?P<id>\d+)/$',YaaasApp_views.view_auction_event, name= 'YaaasApp_view_auction_event'),


    url(r'^list_auction_event/$', YaaasApp_views.list_auction_event,name='YaaasApp_view_list_auction_event'),
    url(r'^search/$', YaaasApp_views.search_auction_events, name='YaaasApp_search_auction_events'),


    url(r'^auction/(?P<auction_event_id>\d+)/bid_set/$', YaaasApp_views.view_bid_history, name='YaaasApp_view_bid_history'),
    url(r'^auction/(?P<auction_event_id>\d+)/ended/$', YaaasApp_views.view_ended_auction_event, name='YaaasApp_view_ended_auction_event'),


    url(r'^auction/(?P<Title>\w+)/edit/$',YaaasApp_views.edit_auction_description, name='YaaasApp_edit_auction_description'),

    (r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^home/setlanguage/$', YaaasApp_views.set_lang, name='YaaasApp_set_lang'),

)



from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()