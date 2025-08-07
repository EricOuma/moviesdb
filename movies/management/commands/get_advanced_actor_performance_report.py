"""
Django Management Command: Comprehensive Actor Performance Analytics Report
This command is intentionally infected with performance issues and memory leaks
for training purposes on optimization techniques.
"""

import gc
import time
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Count, Avg, Q, Prefetch
from django.utils import timezone

from movies.models import Actor, Movie, TVShow, Episode, MovieRating, EpisodeRating, GenreChoices


class Command(BaseCommand):
    help = 'Generate comprehensive actor performance analytics report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file',
            type=str,
            default='actor_analytics_report.txt',
            help='Output file for the report'
        )
        parser.add_argument(
            '--include-detailed-stats',
            action='store_true',
            help='Include detailed statistical analysis'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Actor Performance Analytics Report...'))

        start_time = time.time()

        # MEMORY LEAK #1: Storing all results in memory without cleanup
        self.all_actor_data = []  # This will grow unbounded
        self.cached_ratings = {}  # Never cleared, keeps growing
        self.temporary_calculations = {}  # Another memory hog

        # Get all actors - SYNCHRONOUS ISSUE #1: Should be paginated/chunked
        # This loads ALL actors into memory at once
        actors = list(Actor.objects.all())  # Convert to list loads everything
        self.stdout.write(f'Processing {len(actors)} actors...')

        report_data = self._generate_comprehensive_report(actors, options)
        self._write_report_to_file(report_data, options['output_file'])

        end_time = time.time()
        self.stdout.write(
            self.style.SUCCESS(
                f'Report generated successfully in {end_time - start_time:.2f} seconds'
            )
        )

    def _generate_comprehensive_report(self, actors: List[Actor], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the main analytics report
        PERFORMANCE ISSUE: This method does everything sequentially
        """
        report = {
            'generated_at': timezone.now(),
            'total_actors': len(actors),
            'actor_analytics': [],
            'genre_analysis': {},
            'collaboration_network': {},
            'trend_analysis': {},
        }

        # SYNCHRONOUS ISSUE #2: Processing actors one by one instead of in parallel
        # This could be parallelized using multiprocessing or concurrent.futures
        for i, actor in enumerate(actors):
            if i % 100 == 0:
                self.stdout.write(f'Processing actor {i + 1}/{len(actors)}...')

            # MEMORY LEAK #2: Each iteration adds to memory without cleanup
            actor_data = self._analyze_single_actor(actor, options)
            self.all_actor_data.append(actor_data)  # Memory keeps growing

            # MEMORY LEAK #3: Caching that never expires or cleans up
            self._cache_actor_relationships(actor)

        # SYNCHRONOUS ISSUE #3: Genre analysis done sequentially
        # This should be done in parallel as each genre is independent
        report['genre_analysis'] = self._analyze_genre_performance(actors)

        # SYNCHRONOUS ISSUE #4: Collaboration network analysis
        # This is computationally expensive and should be parallelized
        report['collaboration_network'] = self._analyze_collaboration_network(actors)

        # SYNCHRONOUS ISSUE #5: Trend analysis over time periods
        # Each year could be processed independently
        report['trend_analysis'] = self._analyze_career_trends(actors)

        # MEMORY LEAK #4: Storing processed data in instance variable
        report['actor_analytics'] = self.all_actor_data

        return report

    def _analyze_single_actor(self, actor: Actor, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single actor's performance metrics
        MULTIPLE PERFORMANCE ISSUES HERE
        """
        # SYNCHRONOUS ISSUE #6: Multiple database queries that could be combined
        # Each of these hits the database separately
        movies = actor.movies.all()  # Query 1
        movie_ratings = []

        # SYNCHRONOUS ISSUE #7: N+1 query problem
        # Getting ratings for each movie individually instead of bulk fetch
        for movie in movies:
            ratings = MovieRating.objects.filter(movie=movie)  # N queries!
            movie_ratings.extend(list(ratings))  # MEMORY LEAK #5: Converting to list

        # SYNCHRONOUS ISSUE #8: TV show analysis done sequentially
        tv_episodes = Episode.objects.filter(actors=actor)  # Query 2
        episode_ratings = []

        # SYNCHRONOUS ISSUE #9: Another N+1 query problem
        for episode in tv_episodes:
            ratings = EpisodeRating.objects.filter(episode=episode)  # N more queries!
            episode_ratings.extend(list(ratings))

        # MEMORY LEAK #6: Creating large intermediate data structures
        all_performance_data = {
            'movie_details': [],
            'tv_show_details': [],
            'rating_history': [],
            'genre_performance': {},
            'yearly_breakdown': {},
        }

        # SYNCHRONOUS ISSUE #10: Genre analysis per actor (could be batched)
        for genre in GenreChoices.choices:
            genre_code = genre[0]

            # Separate queries for each genre - very inefficient
            genre_movies = actor.movies.filter(genre=genre_code)  # Query per genre
            genre_episodes = Episode.objects.filter(
                actors=actor,
                season__show__genre=genre_code
            )  # Another query per genre

            # MEMORY LEAK #7: Storing detailed breakdown for each genre
            all_performance_data['genre_performance'][genre_code] = {
                'movies': list(genre_movies.values()),  # Loading all data into memory
                'episodes': list(genre_episodes.values()),  # More memory consumption
                'detailed_ratings': self._get_detailed_ratings(genre_movies, genre_episodes),
            }

        # SYNCHRONOUS ISSUE #11: Yearly breakdown analysis
        # This could be done with a single aggregation query
        current_year = datetime.now().year
        for year in range(1990, current_year + 1):  # 30+ iterations
            yearly_movies = actor.movies.filter(release_date__year=year)  # Query per year
            yearly_episodes = Episode.objects.filter(
                actors=actor,
                air_date__year=year
            )  # Another query per year

            # MEMORY LEAK #8: Storing data for every year even if empty
            all_performance_data['yearly_breakdown'][year] = {
                'movies': list(yearly_movies),
                'episodes': list(yearly_episodes),
                'total_projects': yearly_movies.count() + yearly_episodes.count(),
            }

        # MEMORY LEAK #9: Complex calculations stored permanently
        detailed_stats = self._calculate_detailed_statistics(
            actor, movies, tv_episodes, movie_ratings, episode_ratings
        )

        actor_summary = {
            'id': actor.id,
            'name': actor.full_name,
            'total_movies': len(movies),
            'total_tv_episodes': len(tv_episodes),
            'avg_movie_rating': self._calculate_average_rating(movie_ratings),
            'avg_tv_rating': self._calculate_average_rating(episode_ratings),
            'career_span_years': self._calculate_career_span(actor),
            'genre_diversity': len([g for g in all_performance_data['genre_performance']
                                    if all_performance_data['genre_performance'][g]['movies']
                                    or all_performance_data['genre_performance'][g]['episodes']]),
            'detailed_performance': all_performance_data,  # HUGE memory usage
            'statistical_analysis': detailed_stats,
        }

        # MEMORY LEAK #10: Caching results that are never cleaned
        self.cached_ratings[actor.id] = {
            'movie_ratings': movie_ratings,
            'episode_ratings': episode_ratings,
            'last_calculated': timezone.now(),
        }

        return actor_summary

    def _get_detailed_ratings(self, movies, episodes) -> Dict[str, Any]:
        """
        SYNCHRONOUS ISSUE #12: Could batch these database calls
        """
        detailed_ratings = {
            'movie_ratings': [],
            'episode_ratings': [],
            'rating_distribution': defaultdict(int),
        }

        # SYNCHRONOUS ISSUE #13: Processing each movie individually
        for movie in movies:
            movie_ratings = MovieRating.objects.filter(movie=movie)  # Individual query
            detailed_ratings['movie_ratings'].extend(list(movie_ratings.values()))

        # SYNCHRONOUS ISSUE #14: Processing each episode individually
        for episode in episodes:
            episode_ratings = EpisodeRating.objects.filter(episode=episode)  # Individual query
            detailed_ratings['episode_ratings'].extend(list(episode_ratings.values()))

        return detailed_ratings

    def _calculate_detailed_statistics(self, actor, movies, episodes, movie_ratings, episode_ratings):
        """
        MEMORY LEAK #11: Complex statistical calculations stored in memory
        """
        # MEMORY LEAK #12: Creating large data structures for calculations
        all_ratings_data = []

        # SYNCHRONOUS ISSUE #15: Sequential statistical processing
        for rating in movie_ratings:
            all_ratings_data.append({
                'rating': rating.rating,
                'type': 'movie',
                'content_id': rating.movie.id,
                'date': rating.movie.release_date,
            })

        for rating in episode_ratings:
            all_ratings_data.append({
                'rating': rating.rating,
                'type': 'episode',
                'content_id': rating.episode.id,
                'date': rating.episode.air_date,
            })

        # MEMORY LEAK #13: Storing complex statistical breakdowns
        statistics = {
            'rating_timeline': sorted(all_ratings_data, key=lambda x: x['date']),
            'performance_percentiles': self._calculate_percentiles(all_ratings_data),
            'trend_analysis': self._calculate_trends(all_ratings_data),
            'correlation_data': self._calculate_correlations(actor, all_ratings_data),
        }

        # MEMORY LEAK #14: Caching statistical calculations
        self.temporary_calculations[f'stats_{actor.id}'] = statistics

        return statistics

    def _analyze_genre_performance(self, actors: List[Actor]) -> Dict[str, Any]:
        """
        SYNCHRONOUS ISSUE #16: Genre analysis should be parallelized
        Each genre could be processed independently
        """
        genre_analysis = {}

        for genre_code, genre_name in GenreChoices.choices:
            self.stdout.write(f'Analyzing genre: {genre_name}')

            # SYNCHRONOUS ISSUE #17: Sequential processing of each genre
            # This could be done in parallel threads/processes
            genre_data = {
                'total_actors': 0,
                'top_performers': [],
                'avg_ratings': {},
                'trend_over_time': {},
            }

            # MEMORY LEAK #15: Storing detailed actor data for each genre
            genre_actors_data = []

            # SYNCHRONOUS ISSUE #18: Processing each actor for each genre
            for actor in actors:
                actor_genre_performance = self._analyze_actor_in_genre(actor, genre_code)
                if actor_genre_performance['has_content']:
                    genre_actors_data.append(actor_genre_performance)

            genre_data['total_actors'] = len(genre_actors_data)
            genre_data['detailed_actor_data'] = genre_actors_data  # MEMORY LEAK
            genre_analysis[genre_code] = genre_data

        return genre_analysis

    def _analyze_collaboration_network(self, actors: List[Actor]) -> Dict[str, Any]:
        """
        SYNCHRONOUS ISSUE #19: This is computationally expensive and should be parallelized
        Collaboration analysis has O(n²) complexity and should use parallel processing
        """
        collaboration_data = {
            'actor_pairs': {},
            'most_frequent_collaborators': [],
            'collaboration_success_rates': {},
        }

        # SYNCHRONOUS ISSUE #20: Nested loops create O(n²) complexity done sequentially
        # This could be parallelized by splitting actor pairs across processes
        actor_count = len(actors)
        for i, actor1 in enumerate(actors):
            if i % 50 == 0:
                self.stdout.write(f'Collaboration analysis: {i}/{actor_count}')

            for j, actor2 in enumerate(actors[i + 1:], i + 1):
                # SYNCHRONOUS ISSUE #21: Each pair analysis hits database
                collaboration_info = self._analyze_actor_pair_collaboration(actor1, actor2)

                if collaboration_info['collaborations'] > 0:
                    pair_key = f"{actor1.id}_{actor2.id}"
                    # MEMORY LEAK #16: Storing all collaboration data
                    collaboration_data['actor_pairs'][pair_key] = collaboration_info

        return collaboration_data

    def _analyze_career_trends(self, actors: List[Actor]) -> Dict[str, Any]:
        """
        SYNCHRONOUS ISSUE #22: Career trend analysis should be parallelized
        Each actor's career trend could be calculated independently
        """
        trend_analysis = {
            'overall_industry_trends': {},
            'individual_career_arcs': {},
            'peak_performance_periods': {},
        }

        # SYNCHRONOUS ISSUE #23: Sequential processing of career trends
        for actor in actors:
            career_data = self._calculate_individual_career_trend(actor)
            # MEMORY LEAK #17: Storing detailed career data for every actor
            trend_analysis['individual_career_arcs'][actor.id] = career_data

        return trend_analysis

    def _cache_actor_relationships(self, actor: Actor):
        """
        MEMORY LEAK #18: Caching relationships without cleanup or expiration
        """
        if not hasattr(self, 'relationship_cache'):
            self.relationship_cache = {}

        # MEMORY LEAK #19: Loading and storing all related objects
        self.relationship_cache[actor.id] = {
            'movies': list(actor.movies.all().prefetch_related('ratings')),
            'tv_episodes': list(Episode.objects.filter(actors=actor).prefetch_related('ratings')),
            'directors_worked_with': list(set([
                director for movie in actor.movies.all()
                for director in movie.directors.all()
            ])),
            'cached_at': timezone.now(),
        }

    def _analyze_actor_in_genre(self, actor: Actor, genre_code: str) -> Dict[str, Any]:
        """Helper method for genre analysis"""
        # SYNCHRONOUS ISSUE #24: Individual database queries per actor per genre
        genre_movies = actor.movies.filter(genre=genre_code)
        genre_episodes = Episode.objects.filter(actors=actor, season__show__genre=genre_code)

        return {
            'actor_id': actor.id,
            'has_content': genre_movies.exists() or genre_episodes.exists(),
            'movie_count': genre_movies.count(),
            'episode_count': genre_episodes.count(),
            # MEMORY LEAK #20: Storing full objects instead of just IDs
            'movies': list(genre_movies),
            'episodes': list(genre_episodes),
        }

    def _analyze_actor_pair_collaboration(self, actor1: Actor, actor2: Actor) -> Dict[str, Any]:
        """
        SYNCHRONOUS ISSUE #25: Collaboration analysis with multiple database hits
        """
        # Find shared movies
        shared_movies = actor1.movies.filter(actors=actor2)

        # Find shared TV episodes
        shared_episodes = Episode.objects.filter(actors=actor1).filter(actors=actor2)

        return {
            'collaborations': shared_movies.count() + shared_episodes.count(),
            'shared_movies': list(shared_movies.values()),  # MEMORY LEAK
            'shared_episodes': list(shared_episodes.values()),  # MEMORY LEAK
        }

    def _calculate_individual_career_trend(self, actor: Actor) -> Dict[str, Any]:
        """Calculate career trends for individual actor"""
        # SYNCHRONOUS ISSUE #26: Multiple individual queries per actor
        career_start = actor.movies.order_by('release_date').first()
        latest_work = actor.movies.order_by('-release_date').first()

        return {
            'career_start': career_start.release_date if career_start else None,
            'latest_work': latest_work.release_date if latest_work else None,
            'career_span': (
                                       latest_work.release_date - career_start.release_date).days / 365.25 if career_start and latest_work else 0,
            # MEMORY LEAK #21: Storing detailed yearly breakdown
            'yearly_project_count': self._get_yearly_project_counts(actor),
        }

    def _get_yearly_project_counts(self, actor: Actor) -> Dict[int, int]:
        """
        MEMORY LEAK #22: Creating detailed yearly breakdowns for every actor
        """
        yearly_counts = {}
        current_year = datetime.now().year

        # SYNCHRONOUS ISSUE #27: Individual query per year per actor
        for year in range(1990, current_year + 1):
            movie_count = actor.movies.filter(release_date__year=year).count()
            episode_count = Episode.objects.filter(actors=actor, air_date__year=year).count()
            yearly_counts[year] = movie_count + episode_count

        return yearly_counts

    # Helper methods with performance issues
    def _calculate_average_rating(self, ratings: List) -> Decimal:
        """Simple average calculation with unnecessary complexity"""
        if not ratings:
            return Decimal('0.00')

        # MEMORY LEAK #23: Creating unnecessary data structures
        rating_values = [Decimal(str(r.rating)) for r in ratings]
        total = sum(rating_values)
        return total / Decimal(str(len(rating_values)))

    def _calculate_career_span(self, actor: Actor) -> int:
        """Calculate career span with inefficient queries"""
        # SYNCHRONOUS ISSUE #28: Multiple separate queries instead of one
        first_movie = actor.movies.order_by('release_date').first()
        last_movie = actor.movies.order_by('-release_date').first()

        first_episode = Episode.objects.filter(actors=actor).order_by('air_date').first()
        last_episode = Episode.objects.filter(actors=actor).order_by('-air_date').first()

        dates = []
        if first_movie:
            dates.append(first_movie.release_date)
        if last_movie:
            dates.append(last_movie.release_date)
        if first_episode:
            dates.append(first_episode.air_date)
        if last_episode:
            dates.append(last_episode.air_date)

        if dates:
            return (max(dates) - min(dates)).days // 365
        return 0

    def _calculate_percentiles(self, ratings_data: List[Dict]) -> Dict[str, float]:
        """MEMORY LEAK #24: Unnecessary statistical calculations stored in memory"""
        if not ratings_data:
            return {}

        ratings = sorted([r['rating'] for r in ratings_data])
        return {
            '25th_percentile': self._percentile(ratings, 25),
            '50th_percentile': self._percentile(ratings, 50),
            '75th_percentile': self._percentile(ratings, 75),
            '90th_percentile': self._percentile(ratings, 90),
        }

    def _calculate_trends(self, ratings_data: List[Dict]) -> Dict[str, Any]:
        """MEMORY LEAK #25: Complex trend calculations"""
        # Unnecessarily complex trend analysis that consumes memory
        return {'trend': 'upward', 'slope': 0.1}  # Simplified

    def _calculate_correlations(self, actor: Actor, ratings_data: List[Dict]) -> Dict[str, Any]:
        """MEMORY LEAK #26: Correlation analysis stored in memory"""
        return {'correlation_coefficient': 0.5}  # Simplified

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Simple percentile calculation"""
        if not data:
            return 0.0
        size = len(data)
        return data[int(size * percentile / 100)]

    def _write_report_to_file(self, report_data: Dict[str, Any], output_file: str):
        """
        SYNCHRONOUS ISSUE #29: File writing could be done asynchronously
        MEMORY LEAK #27: Keeping entire report in memory while writing
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPREHENSIVE ACTOR PERFORMANCE ANALYTICS REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Generated at: {report_data['generated_at']}\n")
            f.write(f"Total actors analyzed: {report_data['total_actors']}\n\n")

            # SYNCHRONOUS ISSUE #30: Writing large amounts of data sequentially
            for actor_data in report_data['actor_analytics']:
                f.write(f"Actor: {actor_data['name']}\n")
                f.write(f"  Total Movies: {actor_data['total_movies']}\n")
                f.write(f"  Total TV Episodes: {actor_data['total_tv_episodes']}\n")
                f.write(f"  Average Movie Rating: {actor_data['avg_movie_rating']}\n")
                f.write(f"  Average TV Rating: {actor_data['avg_tv_rating']}\n")
                f.write(f"  Career Span: {actor_data['career_span_years']} years\n")
                f.write(f"  Genre Diversity: {actor_data['genre_diversity']} genres\n")
                f.write("-" * 40 + "\n")

        self.stdout.write(f'Report written to {output_file}')

    def __del__(self):
        """
        MEMORY LEAK #28: Destructor doesn't properly clean up
        These large data structures might not be garbage collected properly
        """
        # This cleanup is insufficient and may not run
        if hasattr(self, 'all_actor_data'):
            del self.all_actor_data
        if hasattr(self, 'cached_ratings'):
            del self.cached_ratings
        if hasattr(self, 'relationship_cache'):
            del self.relationship_cache
