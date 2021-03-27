from django.views.generic.base import TemplateView


class AuthorPage(TemplateView):
    template_name = 'author.html'


class TechPage(TemplateView):
    template_name = 'tech.html'
