from django import template

register = template.Library()


@register.filter
def rating_stars(rating):
    """
    Convert a rating to a list of star states (filled, half, empty)
    Returns a list of 5 tuples: (is_filled, is_half)
    """
    if isinstance(rating, str) or rating is None:
        return [(False, False) for _ in range(5)]
    
    try:
        rating_value = float(rating)
        stars = []
        
        for i in range(5):
            star_position = i + 1
            if star_position <= rating_value:
                stars.append((True, False))  # Filled star
            elif star_position - 0.5 <= rating_value < star_position:
                stars.append((False, True))  # Half star
            else:
                stars.append((False, False))  # Empty star
        
        return stars
    except (ValueError, TypeError):
        return [(False, False) for _ in range(5)]


@register.filter
def format_rating(rating):
    """
    Format rating for display
    """
    if isinstance(rating, str) or rating is None:
        return "No ratings yet"
    
    try:
        rating_value = float(rating)
        return f"{rating_value:.1f}"
    except (ValueError, TypeError):
        return "No ratings yet"


@register.simple_tag(takes_context=True)
def navactive(context, *view_names, class_names="text-movie-red"):
    resolver_match = context['request'].resolver_match
    if resolver_match.url_name in view_names:
        return class_names
    return ""


@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except ValueError:
        try:
            return value - arg
        except TypeError:
            return ""
