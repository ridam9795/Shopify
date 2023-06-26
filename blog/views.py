from django.shortcuts import render
from django.http import HttpResponse
from .models import Blogpost

# Create your views here.
def index(request):
    blogs=Blogpost.objects.all()
    params={'blogs':blogs}
    return render(request, 'blog/index.html',params)
def blogpost(request,id):
    blog=Blogpost.objects.filter(post_id=id)
    print(blog)
    params={'blog':blog[0]}
    return render(request, 'blog/blogpost.html',params)