from django.core.paginator import Paginator

COUNT_PAGES = 10


def paginator_func(request, objects):
    paginator = Paginator(objects, COUNT_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
