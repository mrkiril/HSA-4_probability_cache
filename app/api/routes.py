from aiohttp import web

from . import views

routes = [
    web.view("/article/{article_id}", views.ArticleView, name="article"),
    web.view("/articles", views.ArticlesView, name="articles"),

    web.view("/healthz", views.HealthzCheck, name="health-check"),
    web.view("/favicon.ico", views.Favicon, name="favicon"),
]
