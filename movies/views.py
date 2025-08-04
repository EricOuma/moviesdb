from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Movie, TVShow, Actor, Director, GenreChoices


def home(request):
    """Home page with featured content"""
    # Get featured movies and TV shows
    featured_movies = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).filter(avg_rating__gte=4.0).order_by('-avg_rating')[:6]
    
    featured_tv_shows = TVShow.objects.annotate(
        avg_rating=Avg('seasons__episodes__ratings__rating')
    ).filter(avg_rating__gte=4.0).order_by('-avg_rating')[:6]
    
    # Get latest releases
    latest_movies = Movie.objects.order_by('-release_date')[:8]
    latest_tv_shows = TVShow.objects.order_by('-start_date')[:8]
    
    context = {
        'featured_movies': featured_movies,
        'featured_tv_shows': featured_tv_shows,
        'latest_movies': latest_movies,
        'latest_tv_shows': latest_tv_shows,
    }
    return render(request, 'movies/home.html', context)


def movie_list(request):
    """List all movies with filtering and pagination"""
    movies = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    )
    
    # Filtering
    genre = request.GET.get('genre')
    if genre:
        movies = movies.filter(genre=genre)
    
    search = request.GET.get('search')
    if search:
        movies = movies.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(actors__first_name__icontains=search) |
            Q(actors__last_name__icontains=search) |
            Q(directors__first_name__icontains=search) |
            Q(directors__last_name__icontains=search)
        ).distinct()
    
    # Sorting
    sort_by = request.GET.get('sort', 'title')
    if sort_by == 'rating':
        movies = movies.order_by('-avg_rating')
    elif sort_by == 'release_date':
        movies = movies.order_by('-release_date')
    elif sort_by == 'title':
        movies = movies.order_by('title')
    
    # Pagination
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genres': GenreChoices.choices,
        'current_genre': genre,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'movies/movie_list.html', context)


def movie_detail(request, movie_id):
    """Detailed view of a single movie"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Get similar movies (same genre)
    similar_movies = Movie.objects.filter(
        genre=movie.genre
    ).exclude(id=movie.id)[:6]
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
    }
    return render(request, 'movies/movie_detail.html', context)


def tv_show_list(request):
    """List all TV shows with filtering and pagination"""
    tv_shows = TVShow.objects.annotate(
        avg_rating=Avg('seasons__episodes__ratings__rating'),
        rating_count=Count('seasons__episodes__ratings')
    )
    
    # Filtering
    genre = request.GET.get('genre')
    if genre:
        tv_shows = tv_shows.filter(genre=genre)
    
    search = request.GET.get('search')
    if search:
        tv_shows = tv_shows.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'title')
    if sort_by == 'rating':
        tv_shows = tv_shows.order_by('-avg_rating')
    elif sort_by == 'start_date':
        tv_shows = tv_shows.order_by('-start_date')
    elif sort_by == 'title':
        tv_shows = tv_shows.order_by('title')
    
    # Pagination
    paginator = Paginator(tv_shows, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genres': GenreChoices.choices,
        'current_genre': genre,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'movies/tv_show_list.html', context)


def tv_show_detail(request, tv_show_id):
    """Detailed view of a single TV show"""
    tv_show = get_object_or_404(TVShow, id=tv_show_id)
    
    # Get similar TV shows (same genre)
    similar_tv_shows = TVShow.objects.filter(
        genre=tv_show.genre
    ).exclude(id=tv_show.id)[:6]
    
    context = {
        'tv_show': tv_show,
        'similar_tv_shows': similar_tv_shows,
    }
    return render(request, 'movies/tv_show_detail.html', context)


def actor_list(request):
    """List all actors"""
    actors = Actor.objects.annotate(
        movie_count=Count('movies'),
        tv_episode_count=Count('tv_show_episodes')
    ).order_by('first_name')
    
    # Search
    search = request.GET.get('search')
    if search:
        actors = actors.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(actors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_search': search,
    }
    return render(request, 'movies/actor_list.html', context)


def actor_detail(request, actor_id):
    """Detailed view of a single actor"""
    actor = get_object_or_404(Actor, id=actor_id)
    
    context = {
        'actor': actor,
    }
    return render(request, 'movies/actor_detail.html', context)


def search(request):
    """Global search across movies, TV shows, and actors"""
    query = request.GET.get('q', '')
    min_rating = request.GET.get('min_rating', '')
    max_rating = request.GET.get('max_rating', '')
    year_from = request.GET.get('year_from', '')
    year_to = request.GET.get('year_to', '')
    content_type = request.GET.get('content_type', 'all')  # all, movies, tv_shows, actors
    
    results = {}
    
    if query:
        # Search movies with filters
        movies = Movie.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Apply rating filter for movies
        if min_rating:
            movies = movies.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__gte=float(min_rating))
        if max_rating:
            movies = movies.annotate(avg_rating=Avg('ratings__rating')).filter(avg_rating__lte=float(max_rating))
        
        # Apply year filter for movies
        if year_from:
            movies = movies.filter(release_date__year__gte=int(year_from))
        if year_to:
            movies = movies.filter(release_date__year__lte=int(year_to))
        
        # Search TV shows with filters
        tv_shows = TVShow.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Apply rating filter for TV shows
        if min_rating:
            tv_shows = tv_shows.annotate(avg_rating=Avg('seasons__episodes__ratings__rating')).filter(avg_rating__gte=float(min_rating))
        if max_rating:
            tv_shows = tv_shows.annotate(avg_rating=Avg('seasons__episodes__ratings__rating')).filter(avg_rating__lte=float(max_rating))
        
        # Apply year filter for TV shows
        if year_from:
            tv_shows = tv_shows.filter(start_date__year__gte=int(year_from))
        if year_to:
            tv_shows = tv_shows.filter(start_date__year__lte=int(year_to))
        
        # Search actors
        actors = Actor.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
        
        # Limit results based on content type
        if content_type == 'movies':
            results = {'movies': movies[:20]}
        elif content_type == 'tv_shows':
            results = {'tv_shows': tv_shows[:20]}
        elif content_type == 'actors':
            results = {'actors': actors[:20]}
        else:
            results = {
                'movies': movies[:10],
                'tv_shows': tv_shows[:10],
                'actors': actors[:10],
            }
    
    context = {
        'query': query,
        'min_rating': min_rating,
        'max_rating': max_rating,
        'year_from': year_from,
        'year_to': year_to,
        'content_type': content_type,
        'results': results,
    }
    return render(request, 'movies/search.html', context)
