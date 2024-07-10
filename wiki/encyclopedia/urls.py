from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("wiki/", views.index, name="index"),
    path("wiki/random", views.rndm, name="random"),
    path("wiki/search", views.search, name="search"),
    path("wiki/newpage", views.new, name="new"),
    path("wiki/<str:title>", views.get, name="title"),
    path("wiki/<str:title_name>/editpage", views.edit, name="edit"),
]
