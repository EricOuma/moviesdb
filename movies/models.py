from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, DecimalField, OuterRef, Subquery
from django.db.models.functions import Concat
from django.utils.functional import cached_property


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.GeneratedField(
        expression=Concat(
            "first_name", models.Value(" "), "last_name"
        ),
        output_field=models.CharField(max_length=201),
        db_persist=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

    @cached_property
    def total_movies(self):
        if hasattr(self, 'movies'):
            return self.movies.count()
        return 0


class Actor(Person):
    @property
    def tv_shows(self):
        return TVShow.objects.filter(seasons__episodes__actors=self).distinct()

    @cached_property
    def total_tv_shows(self):
        return self.tv_shows.count()


class Director(Person):

    @property
    def tv_shows(self):
        return TVShow.objects.filter(seasons__episodes__directors=self).distinct()

    @cached_property
    def total_tv_shows(self):
        return self.tv_shows.count()


class GenreChoices(models.TextChoices):
    ACTION = "ACTION", "Action"
    ADVENTURE = "ADVENTURE", "Adventure"
    ANIMATION = "ANIMATION", "Animation"
    COMEDY = "COMEDY", "Comedy"
    CRIME = "CRIME", "Crime"
    DOCUMENTARY = "DOCUMENTARY", "Documentary"
    DRAMA = "DRAMA", "Drama"
    FAMILY = "FAMILY", "Family"
    FANTASY = "FANTASY", "Fantasy"
    HISTORY = "HISTORY", "History"
    HORROR = "HORROR", "Horror"
    KIDS = "KIDS", "Kids"
    MYSTERY = "MYSTERY", "Mystery"
    NEWS = "NEWS", "News"
    REALITY = "REALITY", "Reality"
    ROMANCE = "ROMANCE", "Romance"
    SCI_FI = "SCI_FI", "Sci-Fi"
    SOAP = "SOAP", "Soap"
    TALK = "TALK", "Talk Show"
    THRILLER = "THRILLER", "Thriller"
    WAR = "WAR", "War"
    WESTERN = "WESTERN", "Western"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(
        max_length=20,
        choices=GenreChoices.choices
    )
    release_date = models.DateField()
    duration = models.DurationField()
    actors = models.ManyToManyField(Actor, related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies')
    poster = models.ImageField(upload_to="posters/movies/")

    def __str__(self):
        return self.title

    @property
    def actor_names(self) -> str:
        return ", ".join([actor.name for actor in self.actors.all()])

    @property
    def director_names(self) -> str:
        return ", ".join([director.name for director in self.directors.all()])

    @cached_property
    def rating(self) -> str:
        if not self.ratings.exists():
            return "No ratings yet"

        average_rating = self.ratings.aggregate(Avg('rating', output_field=DecimalField()))['rating__avg']
        return average_rating


class MovieRating(models.Model):
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)


class TVShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(
        max_length=20,
        choices=GenreChoices.choices
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to="posters/movies/")

    def __str__(self):
        return self.title

    @cached_property
    def rating(self) -> Decimal | str:
        # Subquery to get average rating for a single episode
        episode_rating_subquery = EpisodeRating.objects.filter(
            episode=OuterRef('pk')
        ).values('episode').annotate(
            avg_rating=Avg('rating', output_field=DecimalField())
        ).values('avg_rating')[:1]

        episodes_with_ratings_subquery = Episode.objects.filter(
            season=OuterRef('pk')
        ).values('season').annotate(
            avg_rating=Subquery(episode_rating_subquery, output_field=DecimalField())
        ).values('avg_rating')[:1]

        # Annotate each season with its average rating
        seasons_with_ratings = self.seasons.annotate(
            rating=Subquery(episodes_with_ratings_subquery, output_field=DecimalField())
        )

        # Compute the average of those ratings across all episodes
        avg_rating = seasons_with_ratings.aggregate(
            Avg('rating', output_field=DecimalField())
        )['rating__avg']

        if avg_rating == 0:
            return 'No ratings yet'

        return avg_rating

    @property
    def total_episodes(self) -> int:
        total_episodes = 0
        for season in self.seasons.all():
            total_episodes += season.episodes.count()

        return total_episodes


class Season(models.Model):
    show = models.ForeignKey(TVShow, on_delete=models.CASCADE, related_name='seasons')
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, blank=True)
    air_date = models.DateField()

    class Meta:
        ordering = ['number']
        unique_together = ['show', 'number']

    def __str__(self):
        return f"{self.show.title} - Season {self.number}"

    @property
    def rating(self) -> Decimal | str:
        # Subquery to get average rating for a single episode
        episode_rating_subquery = EpisodeRating.objects.filter(
            episode=OuterRef('pk')
        ).values('episode').annotate(
            avg_rating=Avg('rating', output_field=DecimalField())
        ).values('avg_rating')[:1]

        # Annotate each episode with its average rating
        episodes_with_ratings = self.episodes.annotate(
            rating=Subquery(episode_rating_subquery, output_field=DecimalField())
        )

        # Compute the average of those ratings across all episodes
        avg_rating = episodes_with_ratings.aggregate(
            Avg('rating', output_field=DecimalField())
        )['rating__avg']

        if avg_rating == 0:
            return 'No ratings yet'

        return avg_rating


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=255)
    episode_number = models.PositiveSmallIntegerField()
    air_date = models.DateField()
    description = models.TextField()
    duration = models.DurationField()
    actors = models.ManyToManyField(Actor, related_name='tv_show_episodes')
    directors = models.ManyToManyField(Director, related_name='tv_show_episodes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['season', 'episode_number'], name='unique_episode_number_per_season')
        ]

    def __str__(self):
        return self.title

    @property
    def full_title(self):
        return f"S{self.season.number:02d}E{self.episode_number:02d} - {self.title}"

    @cached_property
    def rating(self) -> str:
        if not self.ratings.exists():
            return "No ratings yet"

        average_rating = self.ratings.aggregate(Avg('rating', output_field=DecimalField()))['rating__avg']
        return average_rating


class EpisodeRating(models.Model):
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    episode = models.ForeignKey(Episode, related_name='ratings', on_delete=models.CASCADE)
