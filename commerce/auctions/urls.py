from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new, name="new"),
    path("<int:item_id>", views.listing_pg, name="listing"),
    path("add_watchlist/<int:item_id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.category, name="category"),
    path("place_bid/<int:item_id>", views.place_bid, name="placebid"),
    path("close_bid/<int:item_id>", views.close_bid, name="closebid"),
    path("post_comment/<int:item_id>", views.post_comment, name="postcomment"),
]
