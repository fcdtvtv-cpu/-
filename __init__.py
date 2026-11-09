from . import admin, catalog, reviews, start


def all_routers():
    return [start.router, catalog.router, admin.router, reviews.router]
