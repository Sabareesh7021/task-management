from django.core.paginator import Paginator


def paginate(queryset, request):
    """Paginates a queryset and returns paginated data with the paginator object."""
    page      = request.GET.get('page', 1)
    per_page  = request.GET.get('perPage', 10)
    paginator = Paginator(queryset, per_page)
    
    total_pages = paginator.num_pages
    if page > total_pages:  
        page = total_pages
    
    paginated_data = paginator.get_page(page)
    return {
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": paginated_data.number,
        "data": paginated_data.object_list
    }
    