from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from datetime import timedelta, date
import random
import requests

from movies.models import (
    Actor, Director, Movie, TVShow, Season, Episode, 
    MovieRating, EpisodeRating, GenreChoices
)


class Command(BaseCommand):
    help = 'Populate the database with test data for movies and TV shows'

    def add_arguments(self, parser):
        parser.add_argument(
            '--movies',
            type=int,
            default=500,
            help='Number of movies to create (default: 500)'
        )
        parser.add_argument(
            '--tv-shows',
            type=int,
            default=250,
            help='Number of TV shows to create (default: 250)'
        )

    @transaction.atomic()
    def handle(self, *args, **options):
        self.stdout.write('Starting to populate test data...')
        
        # Create actors and directors first
        actors = self.create_actors()
        directors = self.create_directors()
        
        # Create movies
        movies = self.create_movies(actors, directors, options['movies'])
        
        # Create TV shows with seasons and episodes
        tv_shows = self.create_tv_shows(actors, directors, options['tv_shows'])
        
        # Create ratings for movies and episodes
        self.create_ratings(movies, tv_shows)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(movies)} movies, {len(tv_shows)} TV shows, '
                f'{len(actors)} actors, and {len(directors)} directors with ratings!'
            )
        )

    def create_actors(self):
        """Create 200 actors with realistic names"""
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica',
            'William', 'Amanda', 'James', 'Ashley', 'Christopher', 'Samantha', 'Daniel',
            'Nicole', 'Matthew', 'Stephanie', 'Anthony', 'Rachel', 'Mark', 'Lauren',
            'Donald', 'Megan', 'Steven', 'Amber', 'Paul', 'Brittany', 'Andrew', 'Danielle',
            'Joshua', 'Melissa', 'Kenneth', 'Heather', 'Kevin', 'Elizabeth', 'Brian',
            'Michelle', 'George', 'Kimberly', 'Edward', 'Amy', 'Ronald', 'Angela',
            'Timothy', 'Rebecca', 'Jason', 'Laura', 'Jeffrey', 'Sharon', 'Ryan',
            'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Helen', 'Nicholas', 'Deborah',
            'Eric', 'Lisa', 'Jonathan', 'Nancy', 'Stephen', 'Betty', 'Larry', 'Sandra',
            'Justin', 'Donna', 'Scott', 'Carol', 'Brandon', 'Ruth', 'Benjamin', 'Julie',
            'Samuel', 'Joyce', 'Frank', 'Virginia', 'Gregory', 'Victoria', 'Raymond',
            'Kelly', 'Alexander', 'Joan', 'Patrick', 'Evelyn', 'Jack', 'Lauren',
            'Dennis', 'Judith', 'Jerry', 'Megan', 'Tyler', 'Cheryl', 'Aaron', 'Andrea',
            'Jose', 'Hannah', 'Adam', 'Jacqueline', 'Nathan', 'Martha', 'Henry',
            'Gloria', 'Douglas', 'Teresa', 'Peter', 'Ann', 'Zachary', 'Sara',
            'Walter', 'Madison', 'Kyle', 'Frances', 'Harold', 'Kathryn', 'Carl',
            'Janet', 'Arthur', 'Doris', 'Ryan', 'Gloria', 'Roger', 'Evelyn',
            'Joe', 'Jean', 'Keith', 'Cheryl', 'Samuel', 'Mildred', 'Willie',
            'Katherine', 'Ralph', 'Joan', 'Lawrence', 'Ashley', 'Nicholas', 'Judith',
            'Roy', 'Rose', 'Benjamin', 'Janice', 'Bruce', 'Kelly', 'Brandon',
            'Nicole', 'Adam', 'Judy', 'Harry', 'Christina', 'Fred', 'Kathy',
            'Wayne', 'Theresa', 'Billy', 'Beverly', 'Steve', 'Denise', 'Louis',
            'Tammy', 'Jeremy', 'Irene', 'Aaron', 'Jane', 'Randy', 'Lori',
            'Howard', 'Rachel', 'Eugene', 'Marilyn', 'Carlos', 'Andrea', 'Russell',
            'Lillian', 'Bobby', 'Emily', 'Victor', 'Robin', 'Martin', 'Peggy'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green',
            'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
            'Carter', 'Roberts', 'Gomez', 'Kim', 'Chen', 'Ward', 'Turner',
            'Phillips', 'Parker', 'Evans', 'Edwards', 'Collins', 'Stewart',
            'Sanchez', 'Morris', 'Rogers', 'Reed', 'Cook', 'Morgan', 'Bell',
            'Murphy', 'Bailey', 'Richardson', 'Cox', 'Howard', 'Ward', 'Torres',
            'Peterson', 'Gray', 'Ramirez', 'James', 'Watson', 'Brooks', 'Kelly',
            'Sanders', 'Price', 'Bennett', 'Wood', 'Barnes', 'Ross', 'Henderson',
            'Coleman', 'Jenkins', 'Perry', 'Powell', 'Long', 'Patterson', 'Hughes',
            'Flores', 'Washington', 'Butler', 'Simmons', 'Foster', 'Gonzales',
            'Bryant', 'Alexander', 'Russell', 'Griffin', 'Diaz', 'Hayes'
        ]
        
        actors = []
        for i in range(200):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            actor = Actor(first_name=first_name, last_name=last_name)
            actors.append(actor)

        Actor.objects.bulk_create(actors)
        self.stdout.write(f'Created {len(actors)} actors')
        return actors

    def create_directors(self):
        """Create 100 directors with realistic names"""
        first_names = [
            'Christopher', 'Steven', 'James', 'Quentin', 'Martin', 'David', 'Peter',
            'Ridley', 'Tim', 'Guy', 'Sam', 'Wes', 'Paul', 'Darren', 'Danny',
            'Joel', 'Ethan', 'Coen', 'Robert', 'Zemeckis', 'Ron', 'Howard',
            'George', 'Lucas', 'Francis', 'Ford', 'Coppola', 'Stanley', 'Kubrick',
            'Alfred', 'Hitchcock', 'Orson', 'Welles', 'Akira', 'Kurosawa',
            'Federico', 'Fellini', 'Ingmar', 'Bergman', 'Jean-Luc', 'Godard',
            'François', 'Truffaut', 'Luis', 'Buñuel', 'Yasujirō', 'Ozu',
            'Kenji', 'Mizoguchi', 'Mikio', 'Naruse', 'Masaki', 'Kobayashi',
            'Kon', 'Ichikawa', 'Shohei', 'Imamura', 'Nagisa', 'Oshima',
            'Hiroshi', 'Teshigahara', 'Seijun', 'Suzuki', 'Yoshishige', 'Yoshida',
            'Kiju', 'Yoshida', 'Toshio', 'Matsumoto', 'Shinji', 'Aoyama',
            'Takeshi', 'Kitano', 'Takashi', 'Miike', 'Sion', 'Sono',
            'Hirokazu', 'Kore-eda', 'Naomi', 'Kawase', 'Kiyoshi', 'Kurosawa',
            'Takeshi', 'Kaneshiro', 'Tadanobu', 'Asano', 'Koji', 'Yakusho',
            'Ken', 'Watanabe', 'Hiroyuki', 'Sanada', 'Rinko', 'Kikuchi',
            'Yuko', 'Takeuchi', 'Miki', 'Nakatani', 'Kyoko', 'Fukada',
            'Aoi', 'Miyazaki', 'Rie', 'Miyazawa', 'Yoshino', 'Kimura',
            'Mitsuki', 'Tanimura', 'Yui', 'Aragaki', 'Haruka', 'Ayase',
            'Masami', 'Nagasawa', 'Erika', 'Toda', 'Mirei', 'Kiritani',
            'Nana', 'Eikura', 'Yuka', 'Fujimoto', 'Maki', 'Horikita',
            'Keiko', 'Kitagawa', 'Yuko', 'Takeuchi', 'Miki', 'Nakatani'
        ]
        
        last_names = [
            'Nolan', 'Spielberg', 'Cameron', 'Tarantino', 'Scorsese', 'Fincher',
            'Jackson', 'Scott', 'Burton', 'Ritchie', 'Mendes', 'Anderson',
            'Thomas', 'Anderson', 'Aronofsky', 'Boyle', 'Coen', 'Brothers',
            'Zemeckis', 'Howard', 'Lucas', 'Coppola', 'Kubrick', 'Hitchcock',
            'Welles', 'Kurosawa', 'Fellini', 'Bergman', 'Godard', 'Truffaut',
            'Buñuel', 'Ozu', 'Mizoguchi', 'Naruse', 'Kobayashi', 'Ichikawa',
            'Imamura', 'Oshima', 'Teshigahara', 'Suzuki', 'Yoshida', 'Matsumoto',
            'Aoyama', 'Kitano', 'Miike', 'Sono', 'Kore-eda', 'Kawase',
            'Kurosawa', 'Kaneshiro', 'Asano', 'Yakusho', 'Watanabe', 'Sanada',
            'Kikuchi', 'Takeuchi', 'Nakatani', 'Fukada', 'Miyazaki', 'Miyazawa',
            'Kimura', 'Tanimura', 'Aragaki', 'Ayase', 'Nagasawa', 'Toda',
            'Kiritani', 'Eikura', 'Fujimoto', 'Horikita', 'Kitagawa'
        ]
        
        directors = []
        for i in range(100):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            director = Director(first_name=first_name, last_name=last_name)
            directors.append(director)

        Director.objects.bulk_create(directors)
        self.stdout.write(f'Created {len(directors)} directors')
        return directors

    def create_movies(self, actors, directors, num_movies):
        """Create movies with random data"""
        movie_titles = [
            'The Crimson Horizon', 'Whispers of the Void', 'Eternal Midnight', 'The Last Echo',
            'Shadows of Tomorrow', 'Beyond the Veil', 'The Silent Storm', 'Rising Phoenix',
            'The Forgotten Path', 'Echoes of Destiny', 'The Golden Dawn', 'Midnight Mirage',
            'The Broken Mirror', 'Whispers in the Wind', 'The Last Dance', 'Silent Waters',
            'The Hidden Door', 'Beyond Reality', 'The Lost Treasure', 'Midnight Express',
            'The Silent Storm', 'Eternal Flame', 'The Last Breath', 'Hidden Depths',
            'Beyond Time', 'The Forgotten Kingdom', 'Whispers of Fate', 'The Golden Age',
            'Shadows of the Past', 'The Broken Chain', 'Echoes of Eternity', 'The Last Hope',
            'Silent Echoes', 'The Hidden Truth', 'Beyond Dreams', 'The Lost Horizon',
            'Midnight Magic', 'The Silent Witness', 'Eternal Love', 'The Last Light',
            'Hidden Secrets', 'Beyond the Veil', 'The Forgotten Love', 'Whispers of Hope',
            'The Golden Path', 'Shadows of Light', 'The Broken Heart', 'Echoes of Love',
            'The Last Memory', 'Silent Dreams', 'The Hidden Light', 'Beyond Reality',
            'The Lost Paradise', 'Midnight Stars', 'The Silent Prayer', 'Eternal Peace',
            'The Last Sunset', 'Hidden Beauty', 'Beyond the Moon', 'The Forgotten Dream',
            'Whispers of Peace', 'The Golden Dream', 'Shadows of Hope', 'The Broken Dream',
            'Echoes of Peace', 'The Last Dream', 'Silent Peace', 'The Hidden Dream',
            'Beyond Dreams', 'The Lost Dream', 'Midnight Peace', 'The Silent Dream',
            'Eternal Dream', 'The Last Peace', 'Hidden Dreams', 'Beyond the Dream',
            'The Forgotten Peace', 'Whispers of Dreams', 'The Golden Peace', 'Shadows of Dreams',
            'The Broken Peace', 'Echoes of Dreams', 'The Last Echo', 'Silent Dreams',
            'The Hidden Echo', 'Beyond the Echo', 'The Lost Echo', 'Midnight Echo',
            'The Silent Echo', 'Eternal Echo', 'The Last Echo', 'Hidden Echo',
            'Beyond Echo', 'The Forgotten Echo', 'Whispers of Echo', 'The Golden Echo',
            'Shadows of Echo', 'The Broken Echo', 'Echoes of Echo', 'The Last Shadow',
            'Silent Shadow', 'The Hidden Shadow', 'Beyond the Shadow', 'The Lost Shadow',
            'Midnight Shadow', 'The Silent Shadow', 'Eternal Shadow', 'The Last Shadow',
            'Hidden Shadow', 'Beyond Shadow', 'The Forgotten Shadow', 'Whispers of Shadow',
            'The Crimson Tide', 'Whispers of the Night', 'Eternal Darkness', 'The Last Stand',
            'Shadows of Yesterday', 'Beyond the Stars', 'The Silent Echo', 'Rising Dawn',
            'The Forgotten Path', 'Echoes of Tomorrow', 'The Golden Hour', 'Midnight Dreams',
            'The Broken Mirror', 'Whispers in the Dark', 'The Last Dance', 'Silent Waters',
            'The Hidden Door', 'Beyond Reality', 'The Lost Treasure', 'Midnight Express',
            'The Silent Storm', 'Eternal Flame', 'The Last Breath', 'Hidden Depths',
            'Beyond Time', 'The Forgotten Kingdom', 'Whispers of Fate', 'The Golden Age',
            'Shadows of the Past', 'The Broken Chain', 'Echoes of Eternity', 'The Last Hope',
            'Silent Echoes', 'The Hidden Truth', 'Beyond Dreams', 'The Lost Horizon',
            'Midnight Magic', 'The Silent Witness', 'Eternal Love', 'The Last Light',
            'Hidden Secrets', 'Beyond the Veil', 'The Forgotten Love', 'Whispers of Hope',
            'The Golden Path', 'Shadows of Light', 'The Broken Heart', 'Echoes of Love',
            'The Last Memory', 'Silent Dreams', 'The Hidden Light', 'Beyond Reality',
            'The Lost Paradise', 'Midnight Stars', 'The Silent Prayer', 'Eternal Peace',
            'The Last Sunset', 'Hidden Beauty', 'Beyond the Moon', 'The Forgotten Dream',
            'Whispers of Peace', 'The Golden Dream', 'Shadows of Hope', 'The Broken Dream',
            'Echoes of Peace', 'The Last Dream', 'Silent Peace', 'The Hidden Dream',
            'Beyond Dreams', 'The Lost Dream', 'Midnight Peace', 'The Silent Dream',
            'Eternal Dream', 'The Last Peace', 'Hidden Dreams', 'Beyond the Dream',
            'The Forgotten Peace', 'Whispers of Dreams', 'The Golden Peace', 'Shadows of Dreams',
            'The Broken Peace', 'Echoes of Dreams', 'The Last Echo', 'Silent Dreams',
            'The Hidden Echo', 'Beyond the Echo', 'The Lost Echo', 'Midnight Echo',
            'The Silent Echo', 'Eternal Echo', 'The Last Echo', 'Hidden Echo',
            'Beyond Echo', 'The Forgotten Echo', 'Whispers of Echo', 'The Golden Echo',
            'Shadows of Echo', 'The Broken Echo', 'Echoes of Echo', 'The Last Shadow',
            'Silent Shadow', 'The Hidden Shadow', 'Beyond the Shadow', 'The Lost Shadow',
            'Midnight Shadow', 'The Silent Shadow', 'Eternal Shadow', 'The Last Shadow',
            'Hidden Shadow', 'Beyond Shadow', 'The Forgotten Shadow', 'Whispers of Shadow',
            'The Crimson Dawn', 'Whispers of the Morning', 'Eternal Light', 'The Last Light',
            'Shadows of the Day', 'Beyond the Horizon', 'The Silent Dawn', 'Rising Sun',
            'The Forgotten Light', 'Echoes of the Day', 'The Golden Sun', 'Morning Dreams',
            'The Broken Light', 'Whispers in the Light', 'The Last Light', 'Bright Waters',
            'The Hidden Light', 'Beyond Light', 'The Lost Light', 'Morning Express',
            'The Silent Light', 'Eternal Light', 'The Last Light', 'Bright Depths',
            'Beyond Light', 'The Forgotten Light', 'Whispers of Light', 'The Golden Light',
            'Shadows of Light', 'The Broken Light', 'Echoes of Light', 'The Last Light',
            'Silent Light', 'The Hidden Light', 'Beyond Light', 'The Lost Light',
            'Morning Light', 'The Silent Light', 'Eternal Light', 'The Last Light',
            'Bright Secrets', 'Beyond the Light', 'The Forgotten Light', 'Whispers of Light',
            'The Golden Light', 'Shadows of Light', 'The Broken Light', 'Echoes of Light',
            'The Last Light', 'Silent Light', 'The Hidden Light', 'Beyond Light',
            'The Lost Light', 'Morning Stars', 'The Silent Light', 'Eternal Light',
            'The Last Light', 'Bright Beauty', 'Beyond the Light', 'The Forgotten Light',
            'Whispers of Light', 'The Golden Light', 'Shadows of Light', 'The Broken Light',
            'Echoes of Light', 'The Last Light', 'Silent Light', 'The Hidden Light',
            'Beyond Light', 'The Lost Light', 'Morning Light', 'The Silent Light',
            'Eternal Light', 'The Last Light', 'Bright Dreams', 'Beyond the Light',
            'The Forgotten Light', 'Whispers of Light', 'The Golden Light', 'Shadows of Light',
            'The Broken Light', 'Echoes of Light', 'The Last Light', 'Silent Light',
            'The Hidden Light', 'Beyond the Light', 'The Lost Light', 'Morning Light',
            'The Silent Light', 'Eternal Light', 'The Last Light', 'Bright Echo',
            'Beyond the Light', 'The Forgotten Light', 'Whispers of Light', 'The Golden Light',
            'Shadows of Light', 'The Broken Light', 'Echoes of Light', 'The Last Light',
            'Silent Light', 'The Hidden Light', 'Beyond the Light', 'The Lost Light',
            'Morning Light', 'The Silent Light', 'Eternal Light', 'The Last Light',
            'Bright Shadow', 'Beyond the Light', 'The Forgotten Light', 'Whispers of Light'
        ]
        
        movies = []
        for i in range(num_movies):
            # Random data for movie
            title = random.choice(movie_titles)
            genre = random.choice(GenreChoices.choices)[0]
            release_date = date(1990, 1, 1) + timedelta(days=random.randint(0, 12000))
            duration = timedelta(hours=random.randint(1, 3), minutes=random.randint(0, 59))
            
            movie = Movie.objects.create(
                title=title,
                description=f"A compelling story about {title.lower()} that will keep you on the edge of your seat.",
                genre=genre,
                release_date=release_date,
                duration=duration,
                poster=self.get_random_poster_url()
            )

            # Add random actors and directors
            num_actors = random.randint(10, 20)
            num_directors = random.randint(1, 4)
            
            movie.actors.set(random.sample(actors, min(num_actors, len(actors))))
            movie.directors.set(random.sample(directors, min(num_directors, len(directors))))
            
            movies.append(movie)
        
        self.stdout.write(f'Created {len(movies)} movies')
        return movies

    def create_tv_shows(self, actors, directors, num_tv_shows):
        """Create TV shows with seasons and episodes"""
        tv_show_titles = [
            'Breaking Dawn', 'The Walking Dead', 'Game of Thrones', 'Stranger Things',
            'The Crown', 'The Mandalorian', 'The Witcher', 'Bridgerton',
            'The Queen\'s Gambit', 'Money Heist', 'Dark', 'The Boys',
            'Ozark', 'The Handmaid\'s Tale', 'Westworld', 'The Expanse',
            'The Good Place', 'Brooklyn Nine-Nine', 'The Office', 'Parks and Recreation',
            'Friends', 'Seinfeld', 'The Simpsons', 'Family Guy',
            'South Park', 'Rick and Morty', 'Archer', 'Bob\'s Burgers',
            'Futurama', 'American Dad', 'King of the Hill', 'Beavis and Butt-Head',
            'Daria', 'King of Queens', 'Everybody Loves Raymond', 'Frasier',
            'Cheers', 'Taxi', 'M*A*S*H', 'All in the Family', 'The Mary Tyler Moore Show',
            'The Dick Van Dyke Show', 'I Love Lucy', 'The Honeymooners', 'The Twilight Zone',
            'The Outer Limits', 'Alfred Hitchcock Presents', 'The Andy Griffith Show',
            'Gilligan\'s Island', 'Bewitched', 'I Dream of Jeannie', 'Bewitched',
            'The Addams Family', 'The Munsters', 'The Brady Bunch', 'The Partridge Family',
            'Happy Days', 'Laverne & Shirley', 'Mork & Mindy', 'Welcome Back, Kotter',
            'Barney Miller', 'Taxi', 'WKRP in Cincinnati', 'Soap',
            'The Love Boat', 'Fantasy Island', 'Charlie\'s Angels', 'The Six Million Dollar Man',
            'The Bionic Woman', 'Wonder Woman', 'The Incredible Hulk', 'The Dukes of Hazzard',
            'Dallas', 'Dynasty', 'Knots Landing', 'Falcon Crest', 'Knots Landing',
            'Falcon Crest', 'Dallas', 'Dynasty', 'Knots Landing', 'Falcon Crest',
            'The Crimson Horizon', 'Whispers of the Void', 'Eternal Midnight', 'The Last Echo',
            'Shadows of Tomorrow', 'Beyond the Veil', 'The Silent Storm', 'Rising Phoenix',
            'The Forgotten Path', 'Echoes of Destiny', 'The Golden Dawn', 'Midnight Mirage',
            'The Broken Mirror', 'Whispers in the Wind', 'The Last Dance', 'Silent Waters',
            'The Hidden Door', 'Beyond Reality', 'The Lost Treasure', 'Midnight Express',
            'The Silent Storm', 'Eternal Flame', 'The Last Breath', 'Hidden Depths',
            'Beyond Time', 'The Forgotten Kingdom', 'Whispers of Fate', 'The Golden Age',
            'Shadows of the Past', 'The Broken Chain', 'Echoes of Eternity', 'The Last Hope',
            'Silent Echoes', 'The Hidden Truth', 'Beyond Dreams', 'The Lost Horizon',
            'Midnight Magic', 'The Silent Witness', 'Eternal Love', 'The Last Light',
            'Hidden Secrets', 'Beyond the Veil', 'The Forgotten Love', 'Whispers of Hope',
            'The Golden Path', 'Shadows of Light', 'The Broken Heart', 'Echoes of Love',
            'The Last Memory', 'Silent Dreams', 'The Hidden Light', 'Beyond Reality',
            'The Lost Paradise', 'Midnight Stars', 'The Silent Prayer', 'Eternal Peace',
            'The Last Sunset', 'Hidden Beauty', 'Beyond the Moon', 'The Forgotten Dream',
            'Whispers of Peace', 'The Golden Dream', 'Shadows of Hope', 'The Broken Dream',
            'Echoes of Peace', 'The Last Dream', 'Silent Peace', 'The Hidden Dream',
            'Beyond Dreams', 'The Lost Dream', 'Midnight Peace', 'The Silent Dream',
            'Eternal Dream', 'The Last Peace', 'Hidden Dreams', 'Beyond the Dream',
            'The Forgotten Peace', 'Whispers of Dreams', 'The Golden Peace', 'Shadows of Dreams',
            'The Broken Peace', 'Echoes of Dreams', 'The Last Echo', 'Silent Dreams',
            'The Hidden Echo', 'Beyond the Echo', 'The Lost Echo', 'Midnight Echo',
            'The Silent Echo', 'Eternal Echo', 'The Last Echo', 'Hidden Echo',
            'Beyond Echo', 'The Forgotten Echo', 'Whispers of Echo', 'The Golden Echo',
            'Shadows of Echo', 'The Broken Echo', 'Echoes of Echo', 'The Last Shadow',
            'Silent Shadow', 'The Hidden Shadow', 'Beyond the Shadow', 'The Lost Shadow',
            'Midnight Shadow', 'The Silent Shadow', 'Eternal Shadow', 'The Last Shadow',
            'Hidden Shadow', 'Beyond Shadow', 'The Forgotten Shadow', 'Whispers of Shadow',
            'The Crimson Tide', 'Whispers of the Night', 'Eternal Darkness', 'The Last Stand',
            'Shadows of Yesterday', 'Beyond the Stars', 'The Silent Echo', 'Rising Dawn',
            'The Forgotten Path', 'Echoes of Tomorrow', 'The Golden Hour', 'Midnight Dreams',
            'The Broken Mirror', 'Whispers in the Dark', 'The Last Dance', 'Silent Waters',
            'The Hidden Door', 'Beyond Reality', 'The Lost Treasure', 'Midnight Express',
            'The Silent Storm', 'Eternal Flame', 'The Last Breath', 'Hidden Depths',
            'Beyond Time', 'The Forgotten Kingdom', 'Whispers of Fate', 'The Golden Age',
            'Shadows of the Past', 'The Broken Chain', 'Echoes of Eternity', 'The Last Hope',
            'Silent Echoes', 'The Hidden Truth', 'Beyond Dreams', 'The Lost Horizon',
            'Midnight Magic', 'The Silent Witness', 'Eternal Love', 'The Last Light',
            'Hidden Secrets', 'Beyond the Veil', 'The Forgotten Love', 'Whispers of Hope',
            'The Golden Path', 'Shadows of Light', 'The Broken Heart', 'Echoes of Love',
            'The Last Memory', 'Silent Dreams', 'The Hidden Light', 'Beyond Reality',
            'The Lost Paradise', 'Midnight Stars', 'The Silent Prayer', 'Eternal Peace',
            'The Last Sunset', 'Hidden Beauty', 'Beyond the Moon', 'The Forgotten Dream',
            'Whispers of Peace', 'The Golden Dream', 'Shadows of Hope', 'The Broken Dream',
            'Echoes of Peace', 'The Last Dream', 'Silent Peace', 'The Hidden Dream',
            'Beyond Dreams', 'The Lost Dream', 'Midnight Peace', 'The Silent Dream',
            'Eternal Dream', 'The Last Peace', 'Hidden Dreams', 'Beyond the Dream',
            'The Forgotten Peace', 'Whispers of Dreams', 'The Golden Peace', 'Shadows of Dreams',
            'The Broken Peace', 'Echoes of Dreams', 'The Last Echo', 'Silent Dreams',
            'The Hidden Echo', 'Beyond the Echo', 'The Lost Echo', 'Midnight Echo',
            'The Silent Echo', 'Eternal Echo', 'The Last Echo', 'Hidden Echo',
            'Beyond Echo', 'The Forgotten Echo', 'Whispers of Echo', 'The Golden Echo',
            'Shadows of Echo', 'The Broken Echo', 'Echoes of Echo', 'The Last Shadow',
            'Silent Shadow', 'The Hidden Shadow', 'Beyond the Shadow', 'The Lost Shadow',
            'Midnight Shadow', 'The Silent Shadow', 'Eternal Shadow', 'The Last Shadow',
            'Hidden Shadow', 'Beyond Shadow', 'The Forgotten Shadow', 'Whispers of Shadow',
            'The Crimson Dawn', 'Whispers of the Morning', 'Eternal Light', 'The Last Light',
            'Shadows of the Day', 'Beyond the Horizon', 'The Silent Dawn', 'Rising Sun',
            'The Forgotten Light', 'Echoes of the Day', 'The Golden Sun', 'Morning Dreams',
            'The Broken Light', 'Whispers in the Light', 'The Last Light', 'Bright Waters',
            'The Hidden Light', 'Beyond Light', 'The Lost Light', 'Morning Express',
            'The Silent Light', 'Eternal Light', 'The Last Light', 'Bright Depths',
            'Beyond Light', 'The Forgotten Light', 'Whispers of Light', 'The Golden Light',
            'Shadows of Light', 'The Broken Light', 'Echoes of Light', 'The Last Light',
            'Silent Light', 'The Hidden Light', 'Beyond Light', 'The Lost Light',
            'Morning Light', 'The Silent Light', 'Eternal Light', 'The Last Light',
            'Bright Secrets', 'Beyond the Light', 'The Forgotten Light', 'Whispers of Light',
            'The Golden Light', 'Shadows of Light', 'The Broken Light', 'Echoes of Light',
            'The Last Light', 'Silent Light', 'The Hidden Light', 'Beyond Light',
            'The Lost Light', 'Morning Stars', 'The Silent Light', 'Eternal Light',
            'The Last Light', 'Bright Beauty', 'Beyond the Light', 'The Forgotten Light',
            'Whispers of Light', 'The Golden Light', 'Shadows of Light', 'The Broken Light',
            'Echoes of Light', 'The Last Light', 'Silent Light', 'The Hidden Light',
            'Beyond Light', 'The Lost Light', 'Morning Light', 'The Silent Light',
            'Eternal Light', 'The Last Light', 'Bright Dreams', 'Beyond the Light',
            'The Forgotten Light', 'Whispers of Light', 'The Golden Light', 'Shadows of Light',
            'The Broken Light', 'Echoes of Light', 'The Last Light', 'Silent Light',
            'The Hidden Light', 'Beyond the Light', 'The Lost Light', 'Morning Light',
            'The Silent Light', 'Eternal Light', 'The Last Light', 'Bright Echo',
            'Beyond the Light', 'The Forgotten Light', 'Whispers of Light', 'The Golden Light',
            'Shadows of Light', 'The Broken Light', 'Echoes of Light', 'The Last Light',
            'Silent Light', 'The Hidden Light', 'Beyond the Light', 'The Lost Light',
            'Morning Light', 'The Silent Light', 'Eternal Light', 'The Last Light',
            'Bright Shadow', 'Beyond the Light', 'The Forgotten Light', 'Whispers of Light'
        ]
        
        season_titles = [
            'The Beginning', 'Rising Tides', 'Dark Waters', 'New Horizons', 'Breaking Point',
            'Crossing Lines', 'Hidden Truths', 'Echoes of the Past', 'The Reckoning', 'Lost Souls',
            'Shadows and Light', 'The Awakening', 'Storm Warning', 'Point of No Return', 'The Gathering',
            'Fallen Angels', 'Blood and Fire', 'The Long Road', 'Crossroads', 'The End Times',
            'New Beginnings', 'The Fall', 'Winter\'s End', 'Spring Awakening', 'Summer Heat',
            'Autumn Winds', 'The Deep', 'Surface Tension', 'Breaking Waves', 'Calm Waters', 'Storm Surge',
            'The Hunt', 'The Chase', 'The Escape', 'The Pursuit', 'The Capture',
            'The Trial', 'The Verdict', 'The Sentence', 'The Execution', 'The Aftermath',
            'The Reunion', 'The Separation', 'The Discovery', 'The Revelation', 'The Truth',
            'The Lie', 'The Deception', 'The Betrayal', 'The Redemption', 'The Fall',
            'The Rise', 'The Peak', 'The Valley', 'The Mountain', 'The Ocean',
            'The Desert', 'The Forest', 'The City', 'The Village', 'The Island',
            'The Continent', 'The World', 'The Universe', 'The Galaxy', 'The Cosmos',
            'The Beginning of Time', 'The End of Time', 'The Middle Ages', 'The Modern Era', 'The Future',
            'The Past', 'The Present', 'The Moment', 'The Hour', 'The Day',
            'The Night', 'The Dawn', 'The Dusk', 'The Twilight', 'The Midnight',
            'The Morning', 'The Afternoon', 'The Evening', 'The Sunset', 'The Sunrise',
            'The High Noon', 'The Low Tide', 'The Full Moon', 'The New Moon', 'The Eclipse',
            'The Solar Flare', 'The Meteor Shower', 'The Comet', 'The Asteroid', 'The Black Hole',
            'The White Dwarf', 'The Red Giant', 'The Blue Star', 'The Yellow Sun', 'The Green Planet',
            'The Purple Nebula', 'The Orange Galaxy', 'The Pink Universe', 'The Brown Cosmos', 'The Gray Void'
        ]
        
        episode_titles = [
            'The First Step', 'Crossing the Line', 'Breaking the Rules', 'Finding the Truth', 'Hiding the Secret',
            'Running from the Past', 'Chasing the Future', 'Building the Bridge', 'Burning the Bridge', 'Crossing the River',
            'Climbing the Mountain', 'Descending into Darkness', 'Rising to the Light', 'Falling from Grace', 'Flying to Freedom',
            'Walking the Path', 'Running the Race', 'Swimming the Ocean', 'Diving into the Deep', 'Floating on the Surface',
            'Sinking to the Bottom', 'Rising to the Top', 'Falling to the Ground', 'Climbing to the Sky', 'Descending to Hell',
            'Ascending to Heaven', 'Walking in the Shadows', 'Running in the Light', 'Hiding in the Dark', 'Seeking the Truth',
            'Finding the Lie', 'Telling the Story', 'Hearing the News', 'Seeing the Signs', 'Reading the Signs',
            'Writing the Book', 'Opening the Door', 'Closing the Window', 'Breaking the Lock', 'Fixing the Chain',
            'Cutting the Rope', 'Tying the Knot', 'Untying the Bond', 'Creating the Bond', 'Destroying the Wall',
            'Building the Tower', 'Climbing the Ladder', 'Descending the Stairs', 'Rising the Elevator', 'Falling the Shaft',
            'Flying the Plane', 'Driving the Car', 'Riding the Horse', 'Walking the Dog', 'Running the Cat',
            'Swimming the Fish', 'Flying the Bird', 'Crawling the Snake', 'Slithering the Worm', 'Jumping the Frog',
            'Hopping the Rabbit', 'Galloping the Horse', 'Trotting the Pony', 'Cantering the Mare', 'Galloping the Stallion',
            'Walking the Mule', 'Running the Donkey', 'Flying the Eagle', 'Soaring the Hawk', 'Diving the Falcon',
            'Hunting the Wolf', 'Chasing the Deer', 'Tracking the Bear', 'Following the Fox', 'Catching the Rabbit',
            'Trapping the Mouse', 'Freeing the Bird', 'Caging the Lion', 'Taming the Tiger', 'Training the Dog',
            'Teaching the Cat', 'Learning the Lesson', 'Studying the Book', 'Reading the Page', 'Writing the Word',
            'Speaking the Truth', 'Hearing the Lie', 'Seeing the Light', 'Blind to the Dark', 'Deaf to the Noise',
            'Mute to the Sound', 'Silent to the Voice', 'Loud to the Whisper', 'Quiet to the Shout', 'Soft to the Hard',
            'Gentle to the Rough', 'Kind to the Mean', 'Nice to the Nasty', 'Good to the Bad', 'Right to the Wrong',
            'Correct to the Error', 'True to the False', 'Real to the Fake', 'Genuine to the Phony', 'Authentic to the Counterfeit',
            'Original to the Copy', 'Unique to the Common', 'Special to the Ordinary', 'Extraordinary to the Normal', 'Amazing to the Mundane'
        ]
        
        tv_shows = []
        for i in range(num_tv_shows):
            title = random.choice(tv_show_titles)
            genre = random.choice(GenreChoices.choices)[0]
            start_date = date(1990, 1, 1) + timedelta(days=random.randint(0, 10000))
            end_date = start_date + timedelta(days=random.randint(365, 3650)) if random.random() > 0.3 else None
            
            tv_show = TVShow.objects.create(
                title=title,
                description=f"A groundbreaking series about {title.lower()} that redefined television.",
                genre=genre,
                start_date=start_date,
                end_date=end_date,
                poster=self.get_random_poster_url()
            )

            # Create seasons
            num_seasons = random.randint(3, 10)
            for season_num in range(1, num_seasons + 1):
                season_air_date = start_date + timedelta(days=365 * (season_num - 1))
                season_title = random.choice(season_titles)
                season = Season.objects.create(
                    show=tv_show,
                    number=season_num,
                    title=season_title,
                    air_date=season_air_date
                )
                
                # Create episodes for this season
                num_episodes = random.randint(5, 15)
                for episode_num in range(1, num_episodes + 1):
                    episode_air_date = season_air_date + timedelta(days=7 * (episode_num - 1))
                    episode_title = random.choice(episode_titles)
                    episode = Episode.objects.create(
                        season=season,
                        title=episode_title,
                        episode_number=episode_num,
                        air_date=episode_air_date,
                        description=f"An exciting episode that will keep you guessing.",
                        duration=timedelta(minutes=random.randint(20, 60))
                    )
                    
                    # Add random actors and directors to episode
                    num_actors = random.randint(10, 20)
                    num_directors = random.randint(1, 4)
                    
                    episode.actors.set(random.sample(actors, min(num_actors, len(actors))))
                    episode.directors.set(random.sample(directors, min(num_directors, len(directors))))
            
            tv_shows.append(tv_show)
        
        self.stdout.write(f'Created {len(tv_shows)} TV shows with seasons and episodes')
        return tv_shows

    def create_ratings(self, movies, tv_shows):
        """Create ratings for movies and episodes"""
        # Rate movies
        for movie in movies:
            num_ratings = random.randint(0, 100)
            for _ in range(num_ratings):
                MovieRating.objects.create(
                    movie=movie,
                    rating=random.randint(1, 5)
                )
        
        # Rate episodes
        for tv_show in tv_shows:
            for season in tv_show.seasons.all():
                for episode in season.episodes.all():
                    num_ratings = random.randint(0, 100)
                    for _ in range(num_ratings):
                        EpisodeRating.objects.create(
                            episode=episode,
                            rating=random.randint(1, 5)
                        )
        
        self.stdout.write('Created ratings for all movies and episodes')

    @staticmethod
    def get_random_poster_url():
        """Get a random poster URL from the provided list"""
        poster_urls = [
            'https://media-cache.cinematerial.com/p/500x/ptdwzafa/back-in-action-movie-poster.jpg',
            'https://media-cache.cinematerial.com/p/500x/dmu6uk8v/avatar-the-last-airbender-movie-poster.jpg',
            'https://media-cache.cinematerial.com/p/500x/l94wgadr/f1-the-movie-movie-poster.jpg',
            'https://media-cache.cinematerial.com/p/500x/gbf4hlzz/karate-kid-legends-movie-poster.jpg',
            'https://media-cache.cinematerial.com/p/500x/oqagdh2u/the-beekeeper-movie-poster.jpg'
        ]
        return random.choice(poster_urls)
