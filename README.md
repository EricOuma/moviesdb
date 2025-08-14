# Django Performance Pitfalls Example

This project demonstrates common performance pitfalls in Django applications using a movies and TV shows database as an example. The project intentionally includes various performance issues to help developers understand and identify them.

## Setup

1. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the root of the project and add the following:
```
SECRET_KEY=jg8guguighfihv89g9ufhf9h
DB_NAME=moviesdb
DB_USER=movies_admin
DB_PASSWORD=64C2gsE7qUli
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Load test data:
```bash
python manage.py populate_test_data
```

7. Run the development server:
```bash
python manage.py runserver
```

## Some Performance Pitfalls Demonstrated

### 1. Memory Leaks
- Static cache in `TVShow` model that grows indefinitely
- Large lists being created in memory in the search view
- Inefficient memory usage in episode listing

### 2. Lack of Caching
- No model-level caching for frequently accessed data
- No template fragment caching
- No view caching for expensive operations
- Using DummyCache backend instead of a proper caching solution

### 3. Inefficient Queries
- N+1 query problems in various views
- Multiple separate queries instead of using proper joins
- Inefficient filtering in similar movies query
- Loading all related fields when not needed
- Python-side sorting instead of database-level ordering

### 4. Slow Python Code
- Heavy computations in Python instead of using database features
- Inefficient list operations
- Multiple iterations over querysets
- String operations that could be done at the database level

### 5. Other Issues
- No pagination implemented
- Large text fields without limits
- Unlimited many-to-many relationships
- Inefficient property usage
- Missing database indexes

Running Memray
```bash
 memray run --live -m manage get_simple_actors_performance_report --limit 10 
```

## How to Fix These Issues

Each performance issue is marked with a `# TODO` comment in the code. To fix these issues:

1. **Memory Leaks**:
   - Use Django's caching framework instead of static dictionaries
   - Implement pagination for large result sets
   - Use iterators for large datasets

2. **Caching**:
   - Configure proper cache backend (Redis/Memcached)
   - Use Django's cache decorators
   - Implement template fragment caching
   - Use `cached_property` for expensive computations

3. **Query Optimization**:
   - Use `select_related()` and `prefetch_related()`
   - Combine multiple queries into single queries
   - Add proper database indexes
   - Use database-level operations instead of Python operations

4. **Code Optimization**:
   - Move computations to the database level
   - Use bulk operations
   - Implement proper pagination
   - Use Django's built-in optimization tools

## Monitoring Tools

The project includes Django Debug Toolbar to help identify:
- Number of queries executed
- Time spent in each query
- Template rendering time
- Cache hits and misses

## Contributing

Feel free to add more examples of performance pitfalls or improvements to the existing ones. 