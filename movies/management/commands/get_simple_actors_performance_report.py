"""
Django Management Command: Actor Rating Analysis Report
A focused performance test that runs ~5 minutes but can be optimized to seconds.
Contains critical performance issues for training optimization techniques.
"""

import time
import concurrent.futures
from decimal import Decimal
from typing import Dict, List
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db.models import QuerySet, Avg

from movies.models import Actor, Episode, MovieRating, EpisodeRating

from memory_profiler import profile


class Command(BaseCommand):
    help = 'Generate actor rating analysis report (performance test version)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Number of actors to analyze (default: 500 for ~5min runtime)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Actor Rating Analysis...'))
        start_time = time.time()

        limit = options['limit']
        actors = Actor.objects.all()[:limit]
        self.stdout.write(f'Analyzing {actors.count()} actors...')

        results = self._analyze_all_actors(actors)

        # Generate final report
        self._generate_report(results)

        end_time = time.time()
        self.stdout.write(
            self.style.SUCCESS(f'Analysis completed in {end_time - start_time:.2f} seconds')
        )

    def _analyze_all_actors(self, actors: QuerySet[Actor]) -> List[Dict]:
        """
        SYNCHRONOUS ISSUE #1: Sequential processing - could be parallelized
        This is the main bottleneck that makes it run for 5 minutes
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = []
            future_to_actor = {executor.submit(self._analyze_single_actor, actor): actor for actor in actors}
            for future in concurrent.futures.as_completed(future_to_actor):
                actor = future_to_actor[future]
                try:
                    actor_analysis = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (actor, exc))
                else:
                    results.append(actor_analysis)

        return results

    def _analyze_single_actor(self, actor: Actor) -> Dict:
        """
        Analyze single actor - contains multiple N+1 queries and inefficiencies
        SYNCHRONOUS ISSUE #3: Multiple database hits per actor
        """

        movies = actor.movies.all()
        movie_ratings_data = MovieRating.objects.filter(movie__in=movies)
        movie_avg = movie_ratings_data.aggregate(avg_rating=Avg('rating'))['avg_rating']

        episodes = Episode.objects.filter(actors=actor)
        episode_ratings_data = EpisodeRating.objects.filter(episode__in=episodes)
        episode_avg = episode_ratings_data.aggregate(avg_rating=Avg('rating'))['avg_rating']

        # SYNCHRONOUS ISSUE #11: Genre analysis done per actor instead of bulk
        genre_breakdown = self._analyze_actor_genres(actor, movies, episodes)

        # SYNCHRONOUS ISSUE #12: Collaboration analysis per actor
        collaborations = self._find_collaborations(actor, movies, episodes)

        all_rating_values = (list(movie_ratings_data.values_list('rating', flat=True)) +
                             list(episode_ratings_data.values_list('rating', flat=True)))

        # MEMORY LEAK #10: Store detailed analysis results
        detailed_analysis = {
            'actor_id': actor.id,
            'name': actor.full_name,
            'total_movies': movies.count(),
            'total_episodes': episodes.count(),
            'movie_avg_rating': movie_avg,
            'episode_avg_rating': episode_avg,
            'overall_avg_rating': self._calculate_overall_average(all_rating_values),
            'genre_breakdown': genre_breakdown,  # MEMORY LEAK #11: Detailed genre data
            'collaborations': collaborations,  # MEMORY LEAK #12: Collaboration data
            'rating_distribution': self._calculate_rating_distribution(all_rating_values),
            'career_metrics': self._calculate_career_metrics(actor, movies, episodes),
        }

        return detailed_analysis

    def _calculate_average_rating(self, ratings_data: List) -> Decimal:
        """
        SYNCHRONOUS ISSUE #13: Manual calculation instead of DB aggregation
        This should be done in the database, not in Python
        """
        if not ratings_data:
            return Decimal('0.00')

        # MEMORY LEAK #14: Create unnecessary list comprehension
        rating_values = [Decimal(str(rating)) for rating in ratings_data]

        total = sum(rating_values)  # CPU intensive for large lists
        return total / Decimal(str(len(rating_values)))

    def _analyze_actor_genres(self, actor: Actor, movies: QuerySet, episodes: QuerySet) -> Dict:
        """
        SYNCHRONOUS ISSUE #14: Genre analysis with individual queries
        This could be done with a single aggregation query
        """
        genre_data = defaultdict(lambda: {'movies': 0, 'episodes': 0, 'ratings': []})

        # SYNCHRONOUS ISSUE #15: Process each movie individually for genre analysis
        for movie in movies.prefetch_related('ratings'):
            genre = movie.genre
            genre_data[genre]['movies'] += 1

            # SYNCHRONOUS ISSUE #16: Individual query for movie ratings by genre
            genre_data[genre]['ratings'].extend(list(movie.ratings.all()))  # MEMORY LEAK #15

        # SYNCHRONOUS ISSUE #17: Process each episode individually
        for episode in episodes.select_related('season__show').prefetch_related('ratings'):
            show_genre = episode.season.show.genre  # Potential N+1 if not prefetched
            genre_data[show_genre]['episodes'] += 1
            genre_data[show_genre]['ratings'].extend(list(episode.ratings.all()))  # MEMORY LEAK #16

        # Convert defaultdict to regular dict (MEMORY LEAK #17: keeping all data)
        return dict(genre_data)

    def _find_collaborations(self, actor: Actor, movies: List, episodes: List) -> Dict:
        """
        SYNCHRONOUS ISSUE #20: Collaboration analysis with multiple individual queries
        This creates a huge number of database hits
        """
        collaborators = defaultdict(int)

        # SYNCHRONOUS ISSUE #21: Find movie collaborators one movie at a time
        for movie in movies:
            # SYNCHRONOUS ISSUE #22: Individual query for each movie's other actors
            other_actors = movie.actors.exclude(id=actor.id)  # N+1 query
            for other_actor in other_actors:
                collaborators[other_actor.full_name] += 1

            # SYNCHRONOUS ISSUE #23: Individual query for each movie's directors
            directors = movie.directors.all()  # Another N+1
            for director in directors:
                collaborators[f"Director: {director.full_name}"] += 1

        # SYNCHRONOUS ISSUE #24: Find episode collaborators one episode at a time
        for episode in episodes:
            # SYNCHRONOUS ISSUE #25: Individual query for each episode's other actors
            other_actors = episode.actors.exclude(id=actor.id)  # N+1
            for other_actor in other_actors:
                collaborators[other_actor.full_name] += 1

            # SYNCHRONOUS ISSUE #26: Individual query for each episode's directors
            directors = episode.directors.all()  # N+1
            for director in directors:
                collaborators[f"Director: {director.full_name}"] += 1

        # MEMORY LEAK #18: Convert and store all collaboration data
        return dict(collaborators)

    def _calculate_overall_average(self, all_ratings: List) -> Decimal:
        """
        SYNCHRONOUS ISSUE #27: Inefficient calculation that could be done in DB
        """
        return self._calculate_average_rating(all_ratings)

    def _calculate_rating_distribution(self, ratings_data: List) -> Dict:
        """
        SYNCHRONOUS ISSUE #28: Manual distribution calculation
        This could be done with a single DB aggregation query
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        # MEMORY LEAK #20: Process each rating individually
        for rating in ratings_data:
            distribution[rating] += 1

        return distribution

    def _calculate_career_metrics(self, actor: Actor, movies: List, episodes: List) -> Dict:
        """
        SYNCHRONOUS ISSUE #29: Career metrics with individual date queries
        """
        metrics = {}

        if movies:
            # SYNCHRONOUS ISSUE #30: Sort in Python instead of using DB ordering
            sorted_movies = sorted(movies, key=lambda m: m.release_date)
            metrics['first_movie'] = sorted_movies[0].release_date
            metrics['latest_movie'] = sorted_movies[-1].release_date

        if episodes:
            # SYNCHRONOUS ISSUE #31: Sort episodes in Python instead of DB
            sorted_episodes = sorted(episodes, key=lambda e: e.air_date)
            metrics['first_episode'] = sorted_episodes[0].air_date
            metrics['latest_episode'] = sorted_episodes[-1].air_date

        # SYNCHRONOUS ISSUE #32: Calculate career span in Python
        all_dates = []
        if 'first_movie' in metrics:
            all_dates.extend([metrics['first_movie'], metrics['latest_movie']])
        if 'first_episode' in metrics:
            all_dates.extend([metrics['first_episode'], metrics['latest_episode']])

        if all_dates:
            career_span = (max(all_dates) - min(all_dates)).days
            metrics['career_span_days'] = career_span
            metrics['career_span_years'] = career_span / 365.25

        return metrics

    def _generate_report(self, results: List[Dict]):
        """
        SYNCHRONOUS ISSUE #33: Report generation done sequentially
        This could be done while processing or in parallel
        """
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("ACTOR RATING ANALYSIS REPORT")
        self.stdout.write("=" * 60)

        total_actors = len(results)

        # SYNCHRONOUS ISSUE #34: Calculate summary statistics in Python instead of DB
        total_movies = sum(r['total_movies'] for r in results)
        total_episodes = sum(r['total_episodes'] for r in results)

        # SYNCHRONOUS ISSUE #35: Find top performers by iterating through all results
        top_movie_actors = sorted(
            [r for r in results if r['movie_avg_rating'] > 0],
            key=lambda x: x['movie_avg_rating'],
            reverse=True
        )[:10]

        top_tv_actors = sorted(
            [r for r in results if r['episode_avg_rating'] > 0],
            key=lambda x: x['episode_avg_rating'],
            reverse=True
        )[:10]

        self.stdout.write(f"\nSUMMARY:")
        self.stdout.write(f"Total Actors Analyzed: {total_actors}")
        self.stdout.write(f"Total Movies: {total_movies}")
        self.stdout.write(f"Total Episodes: {total_episodes}")

        self.stdout.write(f"\nTOP 10 MOVIE ACTORS BY RATING:")
        for i, actor in enumerate(top_movie_actors, 1):
            self.stdout.write(
                f"{i:2d}. {actor['name']}: {actor['movie_avg_rating']:.2f} ({actor['total_movies']} movies)")

        self.stdout.write(f"\nTOP 10 TV ACTORS BY RATING:")
        for i, actor in enumerate(top_tv_actors, 1):
            self.stdout.write(
                f"{i:2d}. {actor['name']}: {actor['episode_avg_rating']:.2f} ({actor['total_episodes']} episodes)")
