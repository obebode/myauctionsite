# Create your views here.
from decimal import Decimal
import datetime
import time
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from auction.models import AuctionEvent, AUCTION_ITEM_STATUS_RUNNING, AUCTION_ITEM_STATUS_DISPUTED, Seller, AUCTION_ITEM_STATUS_EXPIRED
from forms import RegistrationForm, AuctionEventForm, confAuction, EditAuctionEventForm, EmailChangeForm, BidForm, AuctionSearchForm
import settings
from utils import process_ended_auction
from yaas import html_to_description


# register new user
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('Yaas_user_home'))
    else:
        form = RegistrationForm(request.POST)

    return render_to_response('register.html', {'form' : form}, context_instance=RequestContext(request))

# the index page of the application
def index(request):
    if request.user.is_authenticated():
        request.session['message'] = ''
        return HttpResponseRedirect(reverse('Yaas_user_home'))
    else:
        return HttpResponseRedirect(reverse('YaaasApp_view_list_auction_event'))

# a logged in user can change his&her password
def password_change(request, post_change_redirect=None,password_change_form=PasswordChangeForm):

    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('Yaas_user_home'))
    else:
        form = password_change_form(user=request.user)

    return render_to_response('password_change_form.html', {'form' : form },  context_instance=RequestContext(request))

def password_change_done(request):
    return password_change_done(request[password_change_done.html ])

# logged in user can change his/her email address
def ChangeEmail(request):
    email = User.objects.get(username = request.user)

    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=email)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('Yaas_user_home'))


    else:
        form = EmailChangeForm(instance=request.user)
        return render_to_response('change_Email.html', {'form' : form },  context_instance=RequestContext(request))


# a logged in user can change his/her user profile information
def edituser(request):
    if not request.user.is_authenticated():
        #return HttpResponseRedirect('/login/?next=%s' %request.path)
        return HttpResponseRedirect('/login/')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('Yaas_user_home') )

    else:
        form = RegistrationForm(instance=request.user)

    return render_to_response('edituser.html', {'form' : form },  context_instance=RequestContext(request))

# Only logged in users can view the home where they can view auctions, bid history, place bid etc
@login_required(login_url='/login/')
def view_user_home(request):
    auction_lists = AuctionEvent.objects.all().order_by('-StartDate')
    won_auctions = AuctionEvent.objects.filter(winning_bidder=request.user, status = AUCTION_ITEM_STATUS_DISPUTED)

    return render_to_response('view_user_home.html', {'auction_lists': auction_lists, 'won_auctions': won_auctions},
                context_instance=RequestContext(request))


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        nextTo = request.GET.get('next', '')            #retrieving the url to redirect after successful login

        user = auth.authenticate(username=username, password=password) #Authenticating the given user

        if user is not None:     #Check whether the user is authentication or not
            auth.login(request,user)    #Loging in the user

            if len(nextTo) != 0:
                return HttpResponseRedirect(nextTo)
            else:
                #return HttpResponseRedirect('/loginpage/')
                return HttpResponseRedirect(reverse('Yaas_user_home'))
    else:
        return render_to_response("login.html", context_instance= RequestContext(request))
    return render_to_response("login.html", {},context_instance= RequestContext(request))


def login_page(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    else:
        return render_to_response("logged_in.html", {'user': request.user.username},context_instance= RequestContext(request))

    return render_to_response('logged_in.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('YaaasApp_view_list_auction_event'))


# registered users can create auction
@login_required(login_url='/login/')
def createauctionConf(request):

    if not request.method == 'POST':
        form =  AuctionEventForm()
        return render_to_response('createauctionConf.html', {'form' : form}, context_instance=RequestContext(request))

    else:
        form = AuctionEventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction_t = cd['Title']
            auction_d = cd['description']
            auction_c = cd['category']
            auction_mp = cd['MinimumPrice']
            auction_sd = cd['StartDate']
            auction_ed = cd['EndDate']

            stdate = datetime.datetime.strftime(auction_sd, '%Y-%m-%d %H:%M')
            #SD = datetime.datetime.strptime(stdate,"%Y-%m-%d %H:%M")

            # Strip the date and time of the start date
            strip_date = str(datetime.datetime.strptime(stdate,"%Y-%m-%d %H:%M").date())
            strip_time = str(datetime.datetime.strptime(stdate,'%Y-%m-%d %H:%M').replace(second=0,microsecond=0).time().strftime('%H:%M'))


            edate = datetime.datetime.strftime(auction_ed, '%Y-%m-%d %H:%M')
            #ED = datetime.datetime.strptime(edate,"%Y-%m-%d %H:%M")

            # Strip the date and time of the end date
            strip_enddate = str(datetime.datetime.strptime(edate,"%Y-%m-%d %H:%M").date())
            strip_endtime = str(datetime.datetime.strptime(edate,'%Y-%m-%d %H:%M').replace(second=0,microsecond=0).time().strftime('%H:%M'))



            form = confAuction()
            return render_to_response('wizardtest.html', {'form' : form, "auction_title" : auction_t, "auction_description" : auction_d,"auction_category": auction_c,
                                                          "auction_minimumprice": auction_mp, "auction_startdate": stdate, "sd":strip_date, "st": strip_time,
                                                          "ed":strip_enddate, "et": strip_endtime,"auction_enddate": edate,
                                                          }, context_instance=RequestContext(request))

        else:
            return render_to_response('createauctionConf.html', {'form' : form, "error" : "Not valid data" },
                context_instance=RequestContext(request))


def saveauctionConf(request):

    option = request.POST.get('option', '')
    if option == 'Yes':
        auction_title = request.POST.get('auction_title', '')
        auction_description = request.POST.get('auction_description','' )
        category = request.POST.get('auction_category', '')
        auction_minimumprice = request.POST.get('auction_minimumprice', '')
        auction_startdate = request.POST.get('strip_date', '')
        auction_startime = request.POST.get('strip_time', '')
        auction_enddate = request.POST.get('strip_enddate', '')
        auction_endtime = request.POST.get('strip_endtime', '')
        sd = datetime.datetime.strptime(auction_startdate,"%Y-%m-%d").date()
        st = datetime.datetime.strptime(auction_startime,"%H:%M").time()
        ed = datetime.datetime.strptime(auction_enddate,"%Y-%m-%d").date()
        et = datetime.datetime.strptime(auction_endtime,"%H:%M").time()
        auction_startdate = datetime.datetime.combine(sd,st)
        auction_enddate = datetime.datetime.combine(ed,et)

        name = User.objects.get(username = request.user)

        auction = AuctionEvent(Title =auction_title, description = auction_description, category = category, MinimumPrice =auction_minimumprice,
         StartDate = auction_startdate, EndDate = auction_enddate,Seller = name)
        auction.save()
        mesg = "New auction has been saved"
        body = "email body"
        from_email = 'noreply@yaas.com'
        to_email = 'customer@yaas.com'
        send_mail('Test Email Subject', body, from_email, [to_email,], fail_silently=False)

        return render_to_response('done.html', {'mesg' : mesg},context_instance=RequestContext(request))

    else:
        error = "Auction is not saved"
        form = AuctionEventForm()
        return render_to_response('createauctionConf.html', {'form' : form, 'error' : error},
            context_instance=RequestContext(request))


@login_required(login_url='/login/')
def create_auction_event(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?next=%s' %request.path)

    if request.method == 'POST':
        auction_form = AuctionEventForm(data=request.POST)

        if auction_form.is_valid():
            auction_event = auction_form.save()
            #return HttpResponseRedirect(reverse('/auction/', args=[auction_event.id]))
            return HttpResponseRedirect(reverse('Yaas_user_home'))
    else:
        auction_form = AuctionEventForm()

    return render_to_response('list_item.html', {
        'auction_form': auction_form
    }, context_instance=RequestContext(request))


# this is the how to create auction without the YES/NO confirmation but this is not really needed for this application
@login_required(login_url='/login/')
def edit_description(request, id):

    a = AuctionEvent.objects.get(pk=int(id))
    if request.method == 'POST':
        form = EditAuctionEventForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/auction/'  )
    else:
        a = AuctionEvent.objects.get(pk=int(id))
        form = EditAuctionEventForm(instance=a)
        return render_to_response('editauction.html', {'form' : form },  context_instance=RequestContext(request))

# resful search webservice api
@csrf_exempt
def apisearch(request, offset):

    auctions = get_object_or_404(AuctionEvent, id = offset,)

    try:
        json = serializers.serialize("json", [auctions])
        response = HttpResponse(json, mimetype="application/json")
        response.status_code = 200
    except (ValueError, TypeError, IndexError):
        response = HttpResponse()
        response.status_code = 400

    return response

# browse and list auction webservice api
@csrf_exempt
def auction_list(request):
    auctions = AuctionEvent.objects.all()
    json = serializers.serialize("json", auctions)
    response = HttpResponse(json, mimetype="application/json")
    response.status_code = 200
    return response


# list of all the auction events that can be seen on the index page as well as the user home
def list_auction_event(request):
    auction_lists = AuctionEvent.objects.all().order_by('-StartDate')
    return render_to_response("archive.html", locals(),context_instance= RequestContext(request))


# this is the bid view the user can see all the descriptions of the auctions and also place bid
@login_required(login_url='/login/')
def view_auction_event(request, id):
    try:
        auction_event = AuctionEvent.objects.get(pk=int(id))
    except AuctionEvent.DoesNotExist:
        raise Http404

    Seller = auction_event.Seller
    bidder = User.objects.get(username = request.user)

    if request.method == 'POST':
        if Seller != bidder:
            form = BidForm(data= request.POST,auction_event = auction_event, bidder= request.user)
            if form.is_valid():
                bid = form.save(commit=False)
                return HttpResponseRedirect(request.get_full_path())
        else:
            return render_to_response("view_auction.html", locals(),
            context_instance=RequestContext(request))
    else:
        form = BidForm(initial={'amount': auction_event.get_current_price() + Decimal('0.01')})

        return render_to_response('view_auction.html',{'form': form,'auction_event': auction_event
        }, context_instance=RequestContext(request))


# This is the basic search nethod to search auctions by title
def search_auction_events(request):
    if request.method == 'POST':
        form = AuctionSearchForm(data = request.POST)
        if form.is_valid():
            found_auctions = form.search()
            return render_to_response('search_results.html', {'found_auctions':
            found_auctions,},context_instance=RequestContext(request))

        else:
            return HttpResponseRedirect(reverse('YaaasApp_view_list_auction_event'))

    else:
        return HttpResponseRedirect(reverse('YaaasApp_view_list_auction_event'))



# Users can also view history before they place bid if they want
def view_bid_history(request, auction_event_id):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404

    bid_set = auction_event.bid_set.all()
    if bid_set.count():
        highest_bid = auction_event.bid_set.order_by('-amount')[0]
    else:
        highest_bid = None

    return render_to_response('view_bid_history.html', {
        'auction_event': auction_event,
        'highest_bid': highest_bid,
        'bid_set': bid_set,
        }, context_instance=RequestContext(request))


# Shows ended auctions and the highest bidder as the winner
def view_ended_auction_event(request, auction_event_id=None):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if not auction_event.is_running():
        process_ended_auction(auction_event)

    return render_to_response('view_ended_auction.html', {
            'auction_event': auction_event
    }, context_instance=RequestContext(request))



# Multiple concurrent feature of editing the description of the auction
def edit_auction_description(request, Title):

    if AuctionEvent.exists(Title):
        #  find an existing auction auction
        auction = AuctionEvent.getByName(Title)

    else:
        # create a new auction event
        auction = AuctionEvent()
        auction.Title = Title
        auction.lockedby = ""

    if auction.lockedby == "":
        # if auction event is not locked, we lock it
        print request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        auction.lockedby=request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        auction.save()

    elif auction.lockedby!=request.COOKIES.get(settings.SESSION_COOKIE_NAME):
        # auction event is locked by others, we return an error message
        return render_to_response("locked.html",
                {'Title': auction.Title, 'description': auction.description},
            context_instance=RequestContext(request) )


        # at this point the auction event is locked by us
    if  request.method == "POST" and\
        request.POST.has_key("description"):
        # a valid POST request: save the new contents of the auction event
        # Always clean the input from the user
        auction.description = html_to_description(request.POST["description"])
        # unlock the auction event
        auction.lockedby=""
        auction.save()
        # Always redirect after a successful POST request
        return HttpResponseRedirect(reverse('Yaas_user_home'))

    else:
        # a GET request or a POST request using the wrong form: show the form
        # kep the article locked by us
        return render_to_response("edit.html",
                {'Title': auction.Title, 'description': auction.description},
            context_instance=RequestContext(request)
        )

# Ban
def ban(request, auction_event_id = None):
    try:
        auction = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if auction.status == "Banned":
        auction.delete()
        auction.save()
        mesg = "this is error"
    return render_to_response("banned.html", {'mesg':mesg},context_instance=RequestContext(request) )

# language switching mechanisms
def set_lang(request):
    from django.utils.translation import check_for_language, activate, to_locale, get_language
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)

    if not next:
        next = '/'
    response = HttpResponseRedirect(next)

    if request.method == 'GET':
        lang_code = request.GET.get('language', None)

        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            translation.activate(lang_code)
    return response



