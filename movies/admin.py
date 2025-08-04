from django.contrib import admin
from movies.models import Actor, Director, Movie, TVShow, Season, Episode, MovieRating, EpisodeRating


class ActorInline(admin.TabularInline):
    model = Movie.actors.through
    extra = 1


class DirectorInline(admin.TabularInline):
    model = Movie.directors.through
    extra = 1


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ['title', 'episode_number', 'air_date', 'duration', 'description']


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 1
    fields = ['number', 'title', 'air_date']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']
    readonly_fields = ['full_name']


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    search_fields = ['first_name', 'last_name']
    readonly_fields = ['full_name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'release_date', 'duration', 'rating', 'poster_preview']
    list_filter = ['genre', 'release_date']
    search_fields = ['title', 'description']
    filter_horizontal = ['actors', 'directors']
    readonly_fields = ['rating', 'poster_preview']
    inlines = [ActorInline, DirectorInline]
    
    def poster_preview(self, obj):
        if obj.poster:
            return f'<img src="{obj.poster}" style="max-height: 50px; max-width: 50px;" />'
        return "No poster"
    poster_preview.short_description = 'Poster'
    poster_preview.allow_tags = True


@admin.register(TVShow)
class TVShowAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'rating', 'poster_preview']
    list_filter = ['genre']
    search_fields = ['title', 'description']
    readonly_fields = ['rating', 'poster_preview']
    inlines = [SeasonInline]
    
    def poster_preview(self, obj):
        if obj.poster:
            return f'<img src="{obj.poster}" style="max-height: 50px; max-width: 50px;" />'
        return "No poster"
    poster_preview.short_description = 'Poster'
    poster_preview.allow_tags = True


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['show', 'number', 'title', 'air_date', 'rating']
    list_filter = ['show', 'air_date']
    search_fields = ['title', 'show__title']
    readonly_fields = ['rating']
    inlines = [EpisodeInline]
