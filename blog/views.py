from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger
from django.utils.log import AdminEmailHandler
from django.views.generic import ListView, DetailView
import logging

from .models import Post, Category

# Create your views here.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('spam.log')
emailHandler = AdminEmailHandler(include_html=True)
logger.addHandler(fh)
logger.addHandler(emailHandler)


# Post Methods

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def list_post(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 5)  # posts each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If the page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    context = {'posts': posts, 'page': page}
    return render(request, 'blog/post/list.html', context)


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html',
                  {'post': post})


# category methods

class CategoryListView(ListView):
    queryset = Category.objects.all()
    context_object_name = 'categories'
    paginate_by = 3
    template_name = 'blog/category/list.html'

def list_categories(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 3)
    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    context = {'categories': categories, 'page': page}
    return render(request, 'blog/category/list.html',
                  context)


class CategoryDetailView(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'blog/category/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object.blog_posts.all()  # add post objects related to category to context
        context['posts'] = post
        return context


def category_details(request, category):
    category = get_object_or_404(Category, slug=category)
    posts = Post.objects.filter(category=category)
    context = {"category": category, "posts": posts}
    return render(request, 'blog/category/detail.html', context)
