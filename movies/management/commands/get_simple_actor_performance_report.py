"""
Django Management Command: Actor Rating Analysis Report
A focused performance test that runs ~5 minutes but can be optimized to seconds.
Contains critical performance issues for training optimization techniques.
"""

import time
from decimal import Decimal
from typing import Dict, List
from collections import defaultdict

from django.core.management.base import BaseCommand

from movies.models import Actor, Episode, MovieRating, EpisodeRating


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

        # MEMORY LEAK #1: Store everything in instance variables that never get cleaned
        self.actor_cache = {}  # Will grow to massive size
        self.rating_cache = {}  # Never cleared
        self.calculation_cache = {}  # Keeps growing

        start_time = time.time()

        # Get actors to analyze
        limit = options['limit']
        actors = list(Actor.objects.all()[:limit])  # MEMORY LEAK #2: Load all into memory
        self.stdout.write(f'Analyzing {len(actors)} actors...')

        # Process each actor individually
        results = self._analyze_all_actors(actors)

        # Generate final report
        self._generate_report(results)

        end_time = time.time()
        self.stdout.write(
            self.style.SUCCESS(f'Analysis completed in {end_time - start_time:.2f} seconds')
        )

    def _analyze_all_actors(self, actors: List[Actor]) -> List[Dict]:
        """
        SYNCHRONOUS ISSUE #1: Sequential processing - could be parallelized
        This is the main bottleneck that makes it run for 5 minutes
        """
        results = []

        for i, actor in enumerate(actors):
            if i % 50 == 0:
                self.stdout.write(f'Processing actor {i + 1}/{len(actors)}...')

            # SYNCHRONOUS ISSUE #2: Each actor processed individually
            # This could be batched or parallelized
            actor_analysis = self._analyze_single_actor(actor)
            results.append(actor_analysis)

            # MEMORY LEAK #3: Cache results without cleanup
            self.actor_cache[actor.id] = actor_analysis

        return results

    def _analyze_single_actor(self, actor: Actor) -> Dict:
        """
        Analyze single actor - contains multiple N+1 queries and inefficiencies
        SYNCHRONOUS ISSUE #3: Multiple database hits per actor
        """

        # SYNCHRONOUS ISSUE #4: Separate query for movies (N+1 problem starts here)
        movies = list(actor.movies.all())  # MEMORY LEAK #4: Convert QuerySet to list

        # SYNCHRONOUS ISSUE #5: Get movie ratings one by one (major N+1 problem)
        movie_ratings_data = []
        for movie in movies:  # This loop creates N queries!
            # SYNCHRONOUS ISSUE #6: Individual query for each movie's ratings
            ratings = list(MovieRating.objects.filter(movie=movie))  # MEMORY LEAK #5
            movie_ratings_data.extend(ratings)

            # MEMORY LEAK #6: Cache each movie's ratings separately
            self.rating_cache[f'movie_{movie.id}'] = ratings

        # SYNCHRONOUS ISSUE #7: Separate query for TV episodes (another N+1)
        episodes = list(Episode.objects.filter(actors=actor))  # MEMORY LEAK #7

        # SYNCHRONOUS ISSUE #8: Get episode ratings one by one (massive N+1 problem)
        episode_ratings_data = []
        for episode in episodes:  # Another loop creating N queries!
            # SYNCHRONOUS ISSUE #9: Individual query for each episode's ratings
            ratings = list(EpisodeRating.objects.filter(episode=episode))  # MEMORY LEAK #8
            episode_ratings_data.extend(ratings)

            # MEMORY LEAK #9: Cache each episode's ratings
            self.rating_cache[f'episode_{episode.id}'] = ratings

        # SYNCHRONOUS ISSUE #10: Calculate statistics individually instead of using DB aggregation
        movie_avg = self._calculate_average_rating(movie_ratings_data)
        episode_avg = self._calculate_average_rating(episode_ratings_data)

        # SYNCHRONOUS ISSUE #11: Genre analysis done per actor instead of bulk
        genre_breakdown = self._analyze_actor_genres(actor, movies, episodes)

        # SYNCHRONOUS ISSUE #12: Collaboration analysis per actor
        collaborations = self._find_collaborations(actor, movies, episodes)

        # MEMORY LEAK #10: Store detailed analysis results
        detailed_analysis = {
            'actor_id': actor.id,
            'name': actor.full_name,
            'total_movies': len(movies),
            'total_episodes': len(episodes),
            'movie_avg_rating': movie_avg,
            'episode_avg_rating': episode_avg,
            'overall_avg_rating': self._calculate_overall_average(movie_ratings_data, episode_ratings_data),
            'genre_breakdown': genre_breakdown,  # MEMORY LEAK #11: Detailed genre data
            'collaborations': collaborations,  # MEMORY LEAK #12: Collaboration data
            'rating_distribution': self._calculate_rating_distribution(movie_ratings_data + episode_ratings_data),
            'career_metrics': self._calculate_career_metrics(actor, movies, episodes),
        }

        # MEMORY LEAK #13: Store in calculation cache
        self.calculation_cache[actor.id] = detailed_analysis

        return detailed_analysis

    def _calculate_average_rating(self, ratings_data: List) -> Decimal:
        """
        SYNCHRONOUS ISSUE #13: Manual calculation instead of DB aggregation
        This should be done in the database, not in Python
        """
        if not ratings_data:
            return Decimal('0.00')

        # MEMORY LEAK #14: Create unnecessary list comprehension
        rating_values = [Decimal(str(rating.rating)) for rating in ratings_data]

        total = sum(rating_values)  # CPU intensive for large lists
        return total / Decimal(str(len(rating_values)))

    def _analyze_actor_genres(self, actor: Actor, movies: List, episodes: List) -> Dict:
        """
        SYNCHRONOUS ISSUE #14: Genre analysis with individual queries
        This could be done with a single aggregation query
        """
        genre_data = defaultdict(lambda: {'movies': 0, 'episodes': 0, 'ratings': []})

        # SYNCHRONOUS ISSUE #15: Process each movie individually for genre analysis
        for movie in movies:
            genre = movie.genre
            genre_data[genre]['movies'] += 1

            # SYNCHRONOUS ISSUE #16: Individual query for movie ratings by genre
            movie_ratings = MovieRating.objects.filter(movie=movie)  # Another N+1!
            genre_data[genre]['ratings'].extend(list(movie_ratings))  # MEMORY LEAK #15

        # SYNCHRONOUS ISSUE #17: Process each episode individually
        for episode in episodes:
            # SYNCHRONOUS ISSUE #18: Individual query to get show genre
            show_genre = episode.season.show.genre  # Potential N+1 if not prefetched
            genre_data[show_genre]['episodes'] += 1

            # SYNCHRONOUS ISSUE #19: Individual query for episode ratings by genre
            episode_ratings = EpisodeRating.objects.filter(episode=episode)  # N+1 again!
            genre_data[show_genre]['ratings'].extend(list(episode_ratings))  # MEMORY LEAK #16

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

    def _calculate_overall_average(self, movie_ratings: List, episode_ratings: List) -> Decimal:
        """
        SYNCHRONOUS ISSUE #27: Inefficient calculation that could be done in DB
        """
        all_ratings = movie_ratings + episode_ratings  # MEMORY LEAK #19: Combine large lists
        return self._calculate_average_rating(all_ratings)

    def _calculate_rating_distribution(self, ratings_data: List) -> Dict:
        """
        SYNCHRONOUS ISSUE #28: Manual distribution calculation
        This could be done with a single DB aggregation query
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        # MEMORY LEAK #20: Process each rating individually
        for rating in ratings_data:
            distribution[rating.rating] += 1

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


# OPTIMIZATION HINTS (commented out for training):

"""
MAJOR OPTIMIZATIONS TO IMPLEMENT:

1. DATABASE OPTIMIZATIONS:
   - Use select_related() and prefetch_related() for all foreign keys
   - Replace N+1 queries with bulk operations
   - Use database aggregations instead of Python calculations
   - Use QuerySet.iterator() for large datasets

2. QUERY OPTIMIZATION:
   Example optimized query:
   actors = Actor.objects.select_related().prefetch_related(
       'movies__ratings',
       'movies__directors', 
       'tv_show_episodes__ratings',
       'tv_show_episodes__directors',
       'tv_show_episodes__season__show'
   ).iterator()

3. AGGREGATION OPTIMIZATION:
   Use Django's database aggregation instead of Python loops:
   - Avg(), Count(), Sum() in queries
   - Annotate QuerySets with calculations

4. PARALLELIZATION:
   - Use multiprocessing.Pool for actor analysis
   - Process chunks of actors in parallel
   - Use concurrent.futures for I/O operations

5. MEMORY OPTIMIZATION:
   - Remove all instance variable caches
   - Use generators instead of lists
   - Process data in chunks
   - Clear intermediate results

With these optimizations, this 5-minute command can run in 10-30 seconds!
"""