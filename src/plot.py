import pandas as pd
import os
from plotly import graph_objects as go
import dash_core_components as dcc


class Plot:
    def __init__(self, filepath, target_column):
        self.filepath = filepath
        self.data = self.read_file()
        self.target_column = target_column
        self.countries = self.data['Country'].unique()
        self.plots = []
        self.figure = None

        self.country_color = {
            'Bahrain': '#bcbd22',
            'Kuwait': '#ff7f0e',
            'Oman': '#2ca02c',
            'Qatar': '#d62728',
            'Saudi Arabia': '#9467bd',
            'United Arab Emirates': '#8c564b',
            'United States': '#e377c2'
        }

        self.feature_colots = {
            'hdi': '#bcbd22',
            'gdp': '#ff7f0e',
            'mortality': '#d62728',
            'incidence': '#8c564b'
        }

    def read_file(self):
        return pd.read_excel(self.filepath)

    def create_scatter(self, country, x='Year', mode=''):
        country_data = self.data[self.data['Country'] == country]
        return go.Scatter(x=country_data[x], y=country_data[self.target_column], mode=mode, name=country,
                          line=dict(color=self.country_color[country]))

    def scatter_all_countries(self, x, y, class_name='', **kwargs):
        self.plots = [self.create_scatter(country, x, mode='lines') for country in self.countries]
        layout = kwargs
        return self.create_graph(self.plots, layout, class_name=class_name)

    @staticmethod
    def create_graph(data, layout, class_name=''):
        return dcc.Graph(figure={'data': data, 'layout': layout}, className=class_name)

# Available Colors in Plotly
# colors = [
#             '#1f77b4',  # muted blue
#             '#ff7f0e',  # safety orange
#             '#2ca02c',  # cooked asparagus green
#             '#d62728',  # brick red
#             '#9467bd',  # muted purple
#             '#8c564b',  # chestnut brown
#             '#e377c2',  # raspberry yogurt pink
#             '#7f7f7f',  # middle gray
#             '#bcbd22',  # curry yellow-green
#             '#17becf'  # blue-teal
#         ]
