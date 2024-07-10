from django import forms
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from markdown2 import markdown
from random import choice
from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={"class" : "text title", "placeholder" : "Title"}))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"class" : "text content", "placeholder" : "Content"}))

class EditPageForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"class" : "text content"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def get(request, title):
    entries= [entry.lower() for entry in util.list_entries()]
    context = {
        "title" : "Not Found", 'entry_valid' : False,
        "content" : f"Sorry, '{title}' does not exist"
    }
    if title.lower() in entries:
        context["title"] = title
        context["entry_valid"] = True
        context["content"] = markdown(util.get_entry(title))
        entry = True
        return render(request, "encyclopedia/entry.html", context)
    
    return render(request, "encyclopedia/entry.html", context)

def search(request):
    if request.method == "GET":
        query = request.GET["q"]
        entries= [entry.lower() for entry in util.list_entries()]
        
        if query.lower() in entries:
            return HttpResponseRedirect(reverse("encyclopedia:title",kwargs={"title":query}))
        elif query == "":
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries()
            })
        results = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "results" : results, "query" : query
        })

def new(request):
    if request.method == "POST":
        nform = NewPageForm(request.POST)
        if nform.is_valid():
            title = nform.cleaned_data["title"]
            content = nform.cleaned_data["content"]
            entries = [entry.lower() for entry in util.list_entries()]
            if title.lower() in entries:
                messages.error(request, "This title already exists.\nPlease add a different one.")
                return render(request, "encyclopedia/newpage.html", {
                    "nform" : nform
                })
            util.save_entry(title, content)
            context = {
                "title" : title,
                "content" : markdown(content)
            }
            return render(request, "encyclopedia/entry.html", context)
    
    return render(request, "encyclopedia/newpage.html", {
        "nform" : NewPageForm()
    })

def edit(request, title_name):
    if request.method == "POST":
        eform = EditPageForm(request.POST)
        if eform.is_valid():
            content = eform.cleaned_data["content"]
            util.save_entry(title_name, content)
            return HttpResponseRedirect(reverse("encyclopedia:title", kwargs={"title" : title_name}))
        
    return render(request, "encyclopedia/editpage.html", {
        "title" : title_name,
        "eform" : EditPageForm(initial={"content" : util.get_entry(title_name)})
    })

def rndm(request):
    title = choice(util.list_entries())
    content = markdown(util.get_entry(title))
    context = {"title" : title, "content" : content, "entry_valid" : True}
    return render(request, "encyclopedia/entry.html", context)