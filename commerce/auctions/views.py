from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import Select, ModelForm, NumberInput, TextInput ,Textarea, ClearableFileInput
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Bid, WatchList, Comment

class ListingForm(ModelForm):
    item_name = forms.CharField(label="Listing Name", widget=TextInput(attrs={"class" : "text form-control"}))
    description = forms.CharField(label="Description", widget=Textarea(attrs={"class" : "text form-control", "id":"desc"}))
    image = forms.ImageField(label="Image Upload", widget=ClearableFileInput(attrs={"class":"img-upload"}), required=False)
    start_bid = forms.IntegerField(label="Starting Bid", widget=NumberInput(attrs={"class":"text form-control"}))
    
    class Meta:
        model = Listing
        fields = ["item_name", "description", "image", "start_bid", "category", "condition"]
        widgets = {
            "category" : Select(attrs={"class":"text form-control"}),
            "condition" : Select(attrs={"class":"text form-control"}),
        }

def index(request):
    listings = Listing.objects.filter(bid_allowed=True)
    listings_info= get_listings_info(listings, request)
    return render(request, "auctions/index.html", {
        "listings_info": listings_info
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new(request):
    if request.method == "POST":
        listing = ListingForm(request.POST, request.FILES)
        if listing.is_valid():
            item_name = listing.cleaned_data["item_name"]
            desc = listing.cleaned_data["description"]
            img = listing.cleaned_data["image"]
            start_bid = listing.cleaned_data["start_bid"]
            category = listing.cleaned_data["category"]
            cond = listing.cleaned_data["condition"]
            new_listing = Listing(
                item_name=item_name, seller=request.user, description=desc, image=img, start_bid=start_bid, category=category, condition=cond
            )
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/newlisting.html", {
        "listing": ListingForm()
    })

def listing_pg(request, item_id):
    listing = Listing.objects.get(pk=item_id)
    context = {"listing":listing, "comments_info":get_comment_info(listing)}
    if listing.bid_exist:
        price = Bid.objects.filter(item=listing).order_by('-bid_amount').first().bid_amount
        highest_bidder = Bid.objects.filter(item=listing).order_by('-bid_amount').first().bidder
        context["highest_bidder"] = highest_bidder
        if not listing.bid_allowed:
            if request.user == highest_bidder:
                messages.success(request, "You have won the auction on this item!")
            else:
                messages.error(request,"Auction on this item has been closed.")
    else: price = listing.start_bid
    context["price"] = price
    if request.user.is_authenticated:
        context["watchlist"] = watchlist_check(listing, request.user)
    return render(request, "auctions/listing.html", context)

@login_required
def add_watchlist(request, item_id):
    item = Listing.objects.get(pk=item_id)
    context = {"listing":item, "comments_info":get_comment_info(item)}
    if item.bid_exist:
        price = Bid.objects.filter(item=item).order_by('-bid_amount').first().bid_amount
        highest_bidder = Bid.objects.filter(item=item).order_by('-bid_amount').first().bidder
        context["highest_bidder"] = highest_bidder
    else: price = item.start_bid
    if request.method == "POST":
        try:
            user_watchlist = WatchList.objects.get(user=request.user)
        except WatchList.DoesNotExist:
            user_watchlist = WatchList(user=request.user)
            user_watchlist.save()
        if WatchList.objects.filter(user=request.user, item=item).exists():
            user_watchlist = WatchList.objects.get(user=request.user,item=item)
            user_watchlist.item.remove(item)
        else: 
            user_watchlist.item.add(item)
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))
    context["price"] = price
    context["watchlist"] = watchlist_check(item, request.user)
    return render(request, "auctions/listing.html", context)

@login_required
def watchlist(request):
    user_watchlist = WatchList.objects.get(user=request.user)
    listings = user_watchlist.item.all()
    listings_info= get_listings_info(listings, request)
    if listings_info == []:
        messages.info(request, "You have not added any items to your Watchlist.")
    return render(request, "auctions/watchlist.html", {
        "listings_info": listings_info
    })

def categories(request):
    listings = Listing.objects.filter(bid_allowed=True)
    categories = Listing.category.field.choices
    category_list = [(c[0],c[1]) for c in categories]
    listings_info= get_listings_info(listings, request)
    return render(request, "auctions/categories.html", {
        "listings_info": listings_info, "categories": category_list
    })

def category(request, category_name):
    listings = Listing.objects.filter(category=category_name)
    categories = Listing.category.field.choices
    cls_active = "btn btn-primary"
    cls_non_active = "btn btn-outline-primary"
    listings_info= get_listings_info(listings, request)
    if listings_info == []:
        messages.info(request, "There are no items in this category.")
    return render(request, "auctions/category.html", {
        "listings_info": listings_info, "categories": categories,
        "cls1": cls_active, "cls2": cls_non_active, "current_category": category_name
    })

@login_required
def place_bid(request, item_id):
    item = Listing.objects.get(pk=item_id)
    context = {"listing":item, "comments_info":get_comment_info(item)}
    if item.bid_exist:
        price = Bid.objects.filter(item=item).order_by('-bid_amount').first().bid_amount
        highest_bidder = Bid.objects.filter(item=item).order_by('-bid_amount').first().bidder
        context["highest_bidder"] = highest_bidder
    else: price = item.start_bid
    if request.method == "POST":
        bid_amount = int(request.POST["bid_amount"])
        if (bid_amount >= price and not item.bid_exist) or (bid_amount > price and item.bid_exist):
            n_bid=Bid(item=item,bidder=request.user,bid_amount=bid_amount)
            n_bid.save()
            item.bid_exist = True
            item.save()
            price = bid_amount
            highest_bidder = Bid.objects.filter(item=item).order_by('-bid_amount').first().bidder
            context["highest_bidder"] = highest_bidder
            try:
                user_watchlist = WatchList.objects.get(user=request.user)
            except WatchList.DoesNotExist:
                user_watchlist = WatchList(user=request.user)
                user_watchlist.save()
            user_watchlist.item.add(item)
        elif bid_amount < price and not item.bid_exist:
            messages.error(request, "You must place a bid which is at least as large as the starting bid.")
        else:
            messages.error(request, "You must place a bid which is higher than the current bid.")
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))
    context["price"] = price
    context["watchlist"] = watchlist_check(item, request.user)
    return render(request, "auctions/listing.html", context)

@login_required
def close_bid(request, item_id):
    item = Listing.objects.get(pk=item_id)
    if request.method == "POST":
        item.bid_allowed = False
        item.save()
    return render(request, "auctions/listing.html", {
        "listing":item
    })

@login_required
def post_comment(request, item_id):
    item = Listing.objects.get(pk=item_id)
    if request.method=="POST":
        commenter=request.user
        comment_content=request.POST["comment"]
        comment=Comment(commenter=commenter, item=item, comment=comment_content)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))
    context = {"listing":item, "comments_info":get_comment_info(item)}
    if item.bid_exist:
        price = Bid.objects.filter(item=item).order_by('-bid_amount').first().bid_amount
        highest_bidder = Bid.objects.filter(item=item).order_by('-bid_amount').first().bidder
        context["highest_bidder"] = highest_bidder
        if not item.bid_allowed:
            if request.user == highest_bidder:
                messages.success(request, "You have won the auction on this item!")
            else:
                messages.error(request,"Auction on this item has been closed.")
    else: price = item.start_bid
    context["price"] = price
    if request.user.is_authenticated:
        context["watchlist"] = watchlist_check(item, request.user)
    return render(request, "auctions/listing.html", context)
        
def watchlist_check(item, user):
    if WatchList.objects.filter(user=user, item=item).exists():
        return True
    else: return False

def get_listings_info(listings, request):
    listings_info=[]
    for listing in listings:
        if listing.bid_exist:
            price=Bid.objects.filter(item=listing).order_by('-bid_amount').first().bid_amount
            highest_bidder=Bid.objects.filter(item=listing).order_by('-bid_amount').first().bidder
            if request.user==highest_bidder:
                row=(listing, price, "My")
            else: row=(listing, price, "Current")
            listings_info.append(row)
        else: 
            listings_info.append((listing, listing.start_bid, "Starting"))
    return listings_info

def get_comment_info(item):
    comments = item.comments.all().order_by("-pk")
    comments_info = []
    for comment in comments:
        comments_info.append((comment.commenter.username, comment.comment))
    return comments_info