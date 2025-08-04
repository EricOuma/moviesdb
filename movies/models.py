from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, DecimalField
from django.db.models.functions import Concat


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


class Actor(Person):
    @property
    def total_movies(self):
        return self.movies.count()

    @property
    def total_tv_shows(self):
        tv_shows_count = 0
        seen_shows = set()
        for episode in self.tv_show_episodes.all():
            if episode.season.show.id not in seen_shows:
                tv_shows_count += 1

        return tv_shows_count


class Director(Person):
    def total_movies(self):
        return self.movies.count()

    @property
    def total_tv_shows(self):
        tv_shows_count = 0
        seen_shows = set()
        for episode in self.tv_show_episodes.all():
            if episode.season.show.id not in seen_shows:
                tv_shows_count += 1

        return tv_shows_count


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

    @property
    def rating(self) -> str:
        if not self.ratings.exists():
            return "No ratings yet"

        average_rating = self.ratings.aggregate(Avg('rating', output_field=DecimalField()))['rating__avg']
        return f"{average_rating:.1f}"


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

    @property
    def rating(self) -> Decimal | str:
        total_rating = 0
        for season in self.seasons.all():
            total_rating += season.rating if isinstance(season.rating, Decimal) else 0

        if total_rating == 0:
            return 'No ratings yet'

        return Decimal(total_rating / self.seasons.count())


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
    def rating(self) -> Decimal|str:
        total_rating = 0
        for episode in self.episodes.all():
            total_rating += episode.rating if isinstance(episode.rating, Decimal) else 0

        if total_rating == 0:
            return 'No ratings yet'

        return Decimal(total_rating/self.episodes.count())


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

    @property
    def rating(self) -> str:
        if not self.ratings.exists():
            return "No ratings yet"

        average_rating = self.ratings.aggregate(Avg('rating', output_field=DecimalField()))['rating__avg']
        return f"{average_rating:.1f}"


class EpisodeRating(models.Model):
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    episode = models.ForeignKey(Episode, related_name='ratings', on_delete=models.CASCADE)
