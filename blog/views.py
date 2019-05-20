from django.shortcuts import render, get_object_or_404
from .models import Post, Category


# Create your views here.

# Post Methods
def list_post(request):
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html',
                  {'post': post})


# category methods
def list_categories(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'blog/category/list.html',
                  context)


def category_details(request, category):
    category = get_object_or_404(Category, slug=category)
    posts = Post.objects.filter(category=category)
    context = {"category": category, "posts": posts}
    return render(request, 'blog/category/detail.html', context)