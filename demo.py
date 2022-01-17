import pandas as pd
import dash
import dash_table
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go



################################################
# get data

# identify NaN values as empty space, don't import NaN values to dataframe
df = pd.read_csv("energeetika.csv", na_values='', keep_default_na=True) 
# here defo better way, remove unnecessary columns
df = df.drop(df.columns[5:], axis=1)
# remove column 
df = df.drop(df.columns[1], axis=1) 
df = df.drop(df.columns[2], axis=1)
# clean up names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '') 

# prepare data for plotting
df['muu_heide'] = (df['koguheide_maakasutuseta_kt_co2_ekv'] - df['energeetika_kt_co2_ekv'])
df['en_protsent'] = (df['energeetika_kt_co2_ekv'] / df['koguheide_maakasutuseta_kt_co2_ekv'] * 100)
df['muu_protsent'] = (100 - df['en_protsent'])


################################################
# create web application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server # need this line for deploying

# define markdown texts
md_top = '''
# Kliimaandmed
  
Interaktiivne rakendus kliimaandmetes orienteerumiseks.
'''
md_dropdown = '''
**Vali graafik:**
'''
md_slider = '''
**Vali ajavahemik:**
'''

md_table = '''
**Andmetabeli alla laadimiseks klõpsa Export:**
'''

md_footnote = '''
*Kasvuhoonegaaside heidet maakasutuse muutustest pole siin arvesse võetud. 
'''


app.layout = dbc.Container([                        # must declare bootstrap theme at top or none of this will work
    # first row for title and subtitle
    dbc.Row([
        html.Div([
            dcc.Markdown(children=md_top, style={'text-align': 'center'})
        ]),
    ]),

    # second row for the graph and its interactive elements
    dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Markdown(children=md_dropdown),
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': 'suhteline heide', 'value': 'protsent'},
                        {'label': 'koguheide', 'value': 'kogu'},
                            ],
                    value='protsent',
                    style={"width": "100%"}),
            ]),  
            align="end",
            width=3
        ),
        dbc.Col(
            html.Div([
                dcc.Markdown(children=md_slider),
                dcc.RangeSlider(
                    id='slider',
                    min=1990,
                    max=2020,
                    step=1,
                    value=[1990,2020],
                    allowCross=False, 
                    tooltip={"placement": "bottom", "always_visible": True})
            ]),
            align="end",
            width=9 
        ) 
    ]),

    dbc.Row([
        html.Div(dcc.Graph(id='graph'))
    ]),

    dbc.Row([
        html.Div([
            dcc.Markdown(children=md_table),
            dash_table.DataTable(
            id='datatable',
            columns=[
                {'name': i, 'id': i}
                for i in df.columns
            ],
            data=df.to_dict('records'),
            export_format='xlsx',
            export_headers='display',
            merge_duplicate_headers=True 
            )
        ])
    ]),

    # row for the footnote
    dbc.Row([
        html.Div(dcc.Markdown(children=md_footnote))
    ])     
])

@app.callback(
    Output('graph', 'figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='slider', component_property='value')]
)

def select_graph(plot_type,year_range):
    df_copy = df.copy()                             # make copy of dataframe
    df_copy = df_copy[df_copy['aasta'].between(year_range[0], year_range[1])]
    # table_data = df_copy.to_dict('records')         # use dataframe to make a dictionary
    # table_columns = [{"name": i, "id": i} for i in df_copy.columns]
    if plot_type == 'protsent':
        fig = px.bar(df_copy,                       # suhteline heide, graafik protsentides
             x='aasta',
             y=['en_protsent','muu_protsent'],
             barmode='stack',
            #  color_discrete_map={
            #  'en_protsent': '#440154',
            #  'muu_protsent': '#5ec962'}, 
             opacity=0.7)
        fig.update_layout(                          # add range slider, comment out if want to use a dash slider
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text='Sektor'
            ),
            modebar_remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
            dragmode=False
        )
        fig.update_yaxes(title_text='Suhteline heide (%)')
        fig.update_xaxes(title_text=None)
        newnames = {'en_protsent':'energeetika', 'muu_protsent': 'muu'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
        return fig
    elif plot_type == 'kogu':
        fig = px.bar(df_copy,                       # absoluutne heide, graafik kt CO2 ekv
             x='aasta',
             y=['energeetika_kt_co2_ekv','muu_heide'],
             barmode='stack',
            #  color_discrete_map={
            #  'energeetika_kt_co2_ekv': '#ABE2FB',
            #  'muu_heide': '#5ec962'}, 
             opacity=0.7)
        fig.update_layout(                          # add range slider, comment out if want to use a dash slider
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text='Sektor'
            ),
            modebar_remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale'],
            dragmode=False
        )
        fig.update_yaxes(title_text='Heide (kt CO2 ekvivalenti)')
        fig.update_xaxes(title_text=None)
        newnames = {'energeetika_kt_co2_ekv':'energeetika', 'muu_heide': 'muu'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
        return fig #, table_data, table_columns

@app.callback(
    Output('datatable', 'data'),
    Input(component_id='slider', component_property='value')
)

def update_table(year_range):
    df_copy = df.copy()                             # make copy of dataframe
    df_copy = df_copy[df_copy['aasta'].between(year_range[0], year_range[1])]
    data = df_copy.to_dict('records')
    return data

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
