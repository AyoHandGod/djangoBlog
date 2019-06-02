import logging
import os

from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, \
    PageNotAnInteger
from django.views.generic import ListView, DetailView, FormView

from logdna import LogDNAHandler

from .models import Post, Category
from .forms import EmailPostForm

# Logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('spam.log')
logDNA = LogDNAHandler(os.environ.get("LOGDNA"))
logger.addHandler(fh)
logger.addHandler(logDNA)

# Create your views here.


# Post Methods

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
    logger.info("Post list viewed", {"app": "djangoBlog"})


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
    logger.info("Post details viewed", {"app": "djangoBlog"})

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
    logger.info("Category list viewed", {"app": "djangoBlog"})


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


class PostShareView(FormView):
    template_name = 'blog/post/share.html'
    context_object_name = 'form'
    form_class = EmailPostForm
    sent = False

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

    def post(self, request, post_id, **kwargs):
        post = get_object_or_404(Post, id=post_id, status="published")
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            subject = '{} ({}) recommends you reading "{}"' \
                .format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}' \
                .format(post.title, post.get_absolute_url(), cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            self.sent = True
            logger.info("Email sent out", {"app": "djangoBlog"})
        else:
            form = EmailPostForm()
        return self.render_to_response(self.get_context_data())


    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        return context


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = '{} ({}) recommends you reading "{}"'\
                .format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'\
                .format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
            logger.info("Email sent out", {"app": "djangoBlog"})
    else:
        form = EmailPostForm()
    context = {'post': post, 'form': form, 'sent': sent}
    return render(request, 'blog/post/share.html', context)
