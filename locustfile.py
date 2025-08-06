import random

from locust import HttpUser, task


class AwesomeUser(HttpUser):
    host = "http://localhost:8300"

    @task
    def home(self):
        self.client.get("/")

    @task
    def movies(self):
        self.client.get("/movies/")

    @task
    def tv_shows(self):
        self.client.get("/tv-shows/")

    @task
    def actors(self):
        self.client.get("/actors/")

    @task
    def directors(self):
        self.client.get("/directors/")

    @task
    def movie_detail(self):
        with self.client.rename_request("/movies/[id]/"):
            for i in random.choices(list(range(500)), k=5):
                self.client.get(f"/movies/{i}/")

    @task
    def tv_show_detail(self):
        with self.client.rename_request("/tv-shows/[id]/"):
            for i in random.choices(list(range(250)), k=5):
                self.client.get(f"/tv-shows/{i}/")

    @task
    def actor_detail(self):
        with self.client.rename_request("/actors/[id]/"):
            for i in random.choices(list(range(200)), k=5):
                self.client.get(f"/actors/{i}/")

    @task
    def director_detail(self):
        with self.client.rename_request("/directors/[id]/"):
            for i in random.choices(list(range(100)), k=5):
                self.client.get(f"/directors/{i}/")

    @task
    def search(self):
        movie_names = ['The Crimson Horizon', 'Whispers of the Void', 'Eternal Midnight', 'The Last Echo']
        tv_show_names = ['Breaking Dawn', 'The Walking Dead', 'Game of Thrones', 'Stranger Things']
        season_titles = ['The Rise', 'The Peak', 'The Valley', 'The Mountain', 'The Ocean']
        episode_titles = ['Writing the Book', 'Opening the Door', 'Closing the Window', 'Breaking the Lock']
        actor_names = ['Tammy', 'Jeremy', 'Irene', 'Aaron', 'Jane', 'Randy', 'Lori']
        director_names = ['Jackson', 'Scott', 'Burton', 'Ritchie', 'Mendes', 'Anderson']

        search_terms = [*movie_names, *tv_show_names, *season_titles, *episode_titles, *actor_names, *director_names]
        content_types = ['all', 'movie', 'tv_shows', 'actors', 'directors']
        rating_choices = list(range(1, 6)) + ['']
        year_choices = list(range(1990, 2024)) + ['']

        with self.client.rename_request(
                "/search/?q=[q]&content_type=[content_type]"
                "&min_rating=[min_rating]&max_rating=[max_rating]"
                "&year_from=[year_from]&year_to=[year_to]"
        ):
            for i in range(10):
                q = random.choice(search_terms)
                content_type = random.choice(content_types)
                min_rating = random.choice(rating_choices)
                max_rating = random.choice(rating_choices)
                year_from = random.choice(year_choices)
                year_to = random.choice(year_choices)

                url = (
                    f"/search/?q={q}&content_type={content_type}"
                    f"&min_rating={min_rating}&max_rating={max_rating}"
                    f"&year_from={year_from}&year_to={year_to}"
                )
                self.client.get(url)
