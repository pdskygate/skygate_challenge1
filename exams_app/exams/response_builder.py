from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BasePaginator(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 10

    def get_counts(self):
        return {
            'count': self.page.paginator.count,
            'pages': self.page.paginator.num_pages
        }


class ResponseBuilder(object):
    SUCCESS_CODE = 200

    def __init__(self, data, paginator=None):
        self.paginator = paginator
        self.data = data
        self.base_response = {
            'result': {
                'value': self.data
            },
            'details': '',
            'status_code': self.SUCCESS_CODE
        }

    def build(self):
        return Response(self.base_response)

    def add_param(self, key, value):
        self.base_response.get('result')[key] = value
        return self

    def paginated_response(self):
        page_data = self.paginator.get_counts()
        self.base_response.get('result')['count'] = page_data.get('count')
        self.base_response.get('result')['pages'] = page_data.get('pages')
        self.base_response.get('result')['next'] = self.paginator.get_next_link()
        self.base_response.get('result')['previous'] = self.paginator.get_previous_link()
        return self
