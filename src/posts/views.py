from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm
from .models import Post
from marketing.models import Signup

def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    # Q allows to use | and & operator on the queryset
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()

    context = {
        'queryset': queryset
    }
    return render(request, 'search_results.html', context)

def get_category_count():
    queryset = Post.objects\
    .values('categories__title').\
    annotate(Count('categories__title'))
    return queryset

def index(request):
    featured = Post.objects.all
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == "POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)

def blog(request):
    category_count = get_category_count()
    # print(category_count)
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    post_list = Post.objects.all()

    # paginator
    paginator = Paginator(post_list, 4)
    # which page to render
    page_request_var = 'page'
    page = request.GET.get(page_request_var)

    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        # last page
        paginated_queryset = paginator.page(paginator.num_pages)

    context =  {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
    }
    return render(request, 'blog.html', context)

def post(request, id):
    post = get_object_or_404(Post, id=id)
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post 
            form.save()
            return redirect('post-detail', id=id)

    context = {
        'post': post,
        'category_count': category_count,
        'most_recent': most_recent,
        'form': form,
    }
    return render(request, 'post1.html', context)