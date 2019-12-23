from . import models


def index_page(request):
    return {'index_page': models.IndexPage.load()}
