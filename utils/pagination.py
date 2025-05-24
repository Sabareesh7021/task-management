from django.core.paginator import Paginator


def paginate(queryset, request):
    """Paginates a queryset and returns paginated data with the paginator object."""
    queryset  = queryset.order_by('-created_at')
    page      = request.GET.get('page', 1)
    per_page  = request.GET.get('perPage', 10)
    paginator = Paginator(queryset, per_page)
    
    page = max(1, min(page, paginator.num_pages))
    
    paginated_data = paginator.get_page(page)
    return {
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": paginated_data.number,
        "data": paginated_data.object_list
    }
    