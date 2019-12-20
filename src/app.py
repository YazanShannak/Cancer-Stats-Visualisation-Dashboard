import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as bootstrap
from dash.dependencies import Input, Output
from src.plot import Plot
from plotly import graph_objects as go
import os
from sklearn.preprocessing import scale
import pandas as pd

# ------------------------------------- Data Init start --------------------------------------------#
data_dir = os.path.join(os.path.curdir, 'data')
data = {
    'hdi': os.path.join(data_dir, 'hdi.xlsx'),
    'gdp': os.path.join(data_dir, 'gdp.xlsx'),
    'mortality': os.path.join(data_dir, 'mortality_rates.xlsx'),
    'incidence': os.path.join(data_dir, 'incidence_rates.xlsx'),
    'hdi_vs_gdp': os.path.join(data_dir, 'hdi_vs_gdp.xlsx')
}

target_columns = {'hdi': 'HDI', 'incidence': 'Incidence Rate', 'mortality': 'Mortality Rate', 'gdp': 'GDP per capita'}
plots = {key: Plot(value, target_columns.get(key)) for key, value in data.items()}
features_options = [{'label': 'GDP per capita', 'value': 'gdp'}, {'label': 'HDI', 'value': 'hdi'},
                    {'label': 'Mortality Rate', 'value': 'mortality'}]

countries_options = [{'label': 'Oman', 'value': 'Oman'}, {'label': 'Saudi Arabia', 'value': 'Saudi Arabia'},
                     {'label': 'United Arab Emirates', 'value': 'United Arab Emirates'},
                     {'label': 'Bahrain', 'value': 'Bahrain'}, {'label': 'Kuwait', 'value': 'Kuwait'},
                     {'label': 'Qatar', 'value': 'Qatar'}, {'label': 'United States', 'value': 'United States'}]
countries_colors = plots.get('hdi').country_color
# ------------------------------------- Data Init end --------------------------------------------#

# ------------------------------------- Main content start --------------------------------------------#
main_header = html.H1('Cancer in United States and the Gulf', className='heading')
main_description = html.P(
    'This dashboard aims to provide visual insights of the state of cancer in the US and the gulf along the years, '
    'in addition to the economic and well-being factors of the population to correlate between the two',
    className='my-3 font-italic')
main_intro = bootstrap.Container(children=[main_header, main_description])
# ------------------------------------- Main content end --------------------------------------------#

# ------------------------------------- Features vs year overall start --------------------------------------------#
overall_hdi_graph = plots.get('hdi').scatter_all_countries('Year', 'HDI', title='HDI',
                                                           class_name='col-lg-6',
                                                           showlegend=True,
                                                           xaxis={'title': ' Year'},
                                                           yaxis={'title': 'HDI'})
overall_mortality_graph = plots.get('mortality').scatter_all_countries('Year', 'Mortality Rate',
                                                                       class_name='col-lg-6',
                                                                       title='Cancer Mortality Rate',
                                                                       showlegend=True,
                                                                       xaxis={'title': ' Year'},
                                                                       yaxis={
                                                                           'title': 'Mortality Rate (deaths per 100,000)'})
overall_gdp_graph = plots.get('gdp').scatter_all_countries('Year', 'GDP per capita', title='GDP', class_name='col-lg-6',
                                                           showlegend=True,
                                                           xaxis={'title': ' Year'},
                                                           yaxis={'title': 'GDP per capita'})
overall_incidence_graph = plots.get('incidence').scatter_all_countries('Year', 'Incidence Rate',
                                                                       class_name='col-lg-6',
                                                                       title='Cancer Incidence Rate',
                                                                       showlegend=True,
                                                                       xaxis={'title': ' Year'},
                                                                       yaxis={
                                                                           'title': 'Incidence Rate (deaths per 100,000)'})
overall_intro = bootstrap.Container(children=[html.H3('Features along the years'), html.P(
    'The following graphs represents the collected features data along the years from about 1990 to 2018',
    className='font-italic')], className='my-3')

overall_features_wrapper = html.Div(
    children=[overall_intro, overall_hdi_graph, overall_mortality_graph, overall_gdp_graph, overall_incidence_graph],
    className='row w-100 p-5 justify-content-center')
# ------------------------------------- Features vs year overall end --------------------------------------------#

# ------------------------------------- Features per country start --------------------------------------------#

feature_country_checklist = dcc.Checklist(id='feature_country_check', options=features_options,
                                          value=['hdi', 'mortality', 'gdp'], className='my-2',
                                          labelClassName='mr-3 ml-1', inputClassName='mr-2')
feature_country_dd = dcc.Dropdown(id='feature_country_dd', options=countries_options,
                                  value='', className='my-2')
feature_country_graph = dcc.Graph(id='feature_country_graph')
feature_per_country_wrapper = bootstrap.Container(
    children=[html.H3('Features per Country'), html.P(
        "You can choose a country and check the features you would like to compare, please note all features values' are standard scaled",
        className='font-italic'),
              feature_country_dd, feature_country_checklist,
              feature_country_graph],
    className='my-4')

# ------------------------------------- Features per country end --------------------------------------------#
# ------------------------------------- HDI vs GDP start --------------------------------------------#
hdi_vs_gdp_data = pd.read_excel(data.get('hdi_vs_gdp'))
hdi_vs_gdp_scatters = []
for country in hdi_vs_gdp_data['Country'].unique():
    country_data = hdi_vs_gdp_data[hdi_vs_gdp_data['Country'] == country]
    hdi_vs_gdp_scatters.append(
        go.Scatter(x=country_data['HDI'], y=country_data['GDP per capita'], mode='markers', text=country_data['Year'],
                   marker_color=countries_colors.get(country), name=country))
hdi_vs_gdp_figure = dict(data=hdi_vs_gdp_scatters,
                         layout=dict(title='HDI vs GDP', xaxis=dict(title='HDI'), yaxis=dict(title='GDP per capita'),
                                     showlegend=True))

hdi_vs_gdp_wrapper = bootstrap.Container(children=[html.H3('HDI vs GDP'), html.P(
    'A plot of GDP per capita vs HDI for each country to determine correaltion between then two',
    className='font-italic'), dcc.Graph(figure=hdi_vs_gdp_figure)])

# ------------------------------------- HDI vs GDP end --------------------------------------------#

# ------------------------------------- app configuration start --------------------------------------------#
app = dash.Dash(external_stylesheets=[bootstrap.themes.BOOTSTRAP])
app.title = 'Cancer Statistics'
main = html.Div(children=[main_intro, overall_features_wrapper, feature_per_country_wrapper, hdi_vs_gdp_wrapper],
                className='my-4')
app.layout = main


# ------------------------------------- app configuration end --------------------------------------------#

# ------------------------------------- app callbacks start --------------------------------------------#
## feature per country
@app.callback(Output('feature_country_graph', 'figure'),
              [Input('feature_country_check', 'value'), Input('feature_country_dd', 'value')])
def feature_country_callback(selected_features, selected_country):
    scatters = []

    for feature in selected_features:
        data = plots.get(feature).data
        country_data = data[data['Country'] == selected_country]
        target_column = target_columns.get(feature)
        target_values = country_data[target_column].to_numpy()

        scatter = go.Scatter(x=country_data['Year'],
                             y=scale(country_data[target_column].to_numpy()),
                             name=target_column, mode='lines')
        scatters.append(scatter)
    return {'data': scatters}


# ------------------------------------- app callbacks end --------------------------------------------#

server = app.server

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5000)
