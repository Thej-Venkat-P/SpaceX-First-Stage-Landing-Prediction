# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Dataframe
spacex_df = pd.read_csv("data_falcon9_2.csv")
max_payload = spacex_df['PayloadMass'].max()
min_payload = spacex_df['PayloadMass'].min()

# Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}
                                        ),
                                # Dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'All Sites'},
                                    {'label': 'CCSFS SLC 40', 'value': 'CCSFS SLC 40'},
                                    {'label': 'VAFB SLC 4E', 'value': 'VAFB SLC 4E'},
                                    {'label': 'KSC LC 39A', 'value': 'KSC LC 39A'}
                                ],
                                placeholder='Select a Launch Site Here',
                                value='All Sites',
                                searchable=True
                                ),
                                html.Br(),

                                # Pie chart to show the total successful launches count for all sites
                                # Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
                                value=[min_payload, max_payload]),

                                # Scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(launch_site):
    if launch_site == 'All Sites':
        fig = px.pie(values=spacex_df.groupby('LaunchSite')['Class'].mean(), 
                     names=spacex_df.groupby('LaunchSite')['LaunchSite'].first(),
                     title='Total Success Launches by Site')
    else:
        fig = px.pie(values=spacex_df[spacex_df['LaunchSite']==str(launch_site)]['Class'].value_counts(normalize=True), 
                     names=spacex_df['Class'].unique(), 
                     title='Total Success Launches for Site {}'.format(launch_site))
    return(fig)


@app.callback( Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider',component_property='value')])
def get_payload_chart(launch_site, payload_mass):
    if launch_site == 'All Sites':
        fig = px.scatter(spacex_df[spacex_df['PayloadMass'].between(payload_mass[0], payload_mass[1])], 
                x="PayloadMass",
                y="Class",
                color="BoosterVersion",
                hover_data=['LaunchSite'],
                title='Correlation Between Payload and Success for All Sites')
    else:
        df = spacex_df[spacex_df['LaunchSite']==str(launch_site)]
        fig = px.scatter(df[df['PayloadMass'].between(payload_mass[0], payload_mass[1])], 
                x="PayloadMass",
                y="Class",
                color="BoosterVersion",
                hover_data=['LaunchSite'],
                title='Correlation Between Payload and Success for Site {}'.format(launch_site))
    return(fig)


if __name__ == '__main__':
    app.run_server()
