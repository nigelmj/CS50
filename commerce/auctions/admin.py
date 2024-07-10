from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "date_joined")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "item_name", "seller")

admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(WatchList)
admin.site.register(Comment)