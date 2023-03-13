from django.db import models
from wagtail.models import Page
import plotly.express as px

class HomePage(Page):
    template = 'home/home_page.html'

    # @property
    # def plot(self):
    #     data_canada = px.data.gapminder().query("country == 'Canada'")
    #     fig = px.bar(data_canada, x='year', y='pop', title='Test Graph')
    #     return fig.to_html(full_html=False)

