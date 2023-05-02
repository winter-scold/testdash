#!/usr/bin/env python
# coding: utf-8

# # 1. Import Modules

# In[1]:


import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.offline as pyo
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
from plotly.subplots import make_subplots

import geojson
import json

import datetime as dt
label = dt.date.today().strftime("%d")

import statsmodels.api as sm

import dash_bootstrap_templates 
import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output, callback

import dash_auth



# ### Define Username/Password for Log-in and importing external stylesheet for theme

# In[2]:


USERNAME_PASSWORD_PAIRS = [
    ['Zemo', 'letmein'],['Zemo', 'password']
]

#heroku pass is Zemo123!

#Initialising application and importing external stylesheets for global theme
app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.CERULEAN, "https://fonts.googleapis.com/css?family=Poppins&display=swap"],
    suppress_callback_exceptions=True,
    show_undo_redo=False)


#app = Dash(__name__, suppress_callback_exceptions=True)


auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)

server = app.server


# # 2. Define Plot Themes
# 
# Three themes based on Zemo colors:
# 1. Graphs
# 2. Range slider
# 3. Choropleths

# In[3]:


## Zemo Graph Template Theme (w/ spikes on hover)

#label_annex = str(28)
#if label != label_annex:
cw = ['#00A8E0', '#0070C4', '#42B029', '#007526','#001A70'] + px.colors.qualitative.Vivid_r
#else:
#    cw = ['#ffffff', '#ffffff', '#ffffff', '#ffffff','#ffffff']
    
## Zemo Graph Template Theme
zemo_template = dict(
    layout=go.Layout(
                    title_x = 0, title_xanchor = 'left', title_xref = 'paper', 
                    title_font=dict(family="Arial", size=20), 
                     font=dict(family="Arial", size=14),
                     plot_bgcolor='White',
                     paper_bgcolor = 'White',
                     colorway = cw,
                     xaxis = dict(linecolor = 'black', 
                                  showline= True, linewidth= 1, tickangle = 30, ticks='outside', gridcolor='Lavenderblush', ticklabelmode = 'instant', showgrid = True),
                     yaxis = dict(linecolor = 'black', showline=True, linewidth = 1, tickangle = 0, gridcolor='Lavenderblush', ticklabelmode = 'instant', showgrid = True),
                     legend = dict(bgcolor = 'whitesmoke', bordercolor = 'grey', borderwidth = 1)
                    )
                    )

## Zemo Graph Template Theme (w/ spikes on hover)
zemo_template_spike = dict(
    layout=go.Layout(
                    title_x = 0, title_xanchor = 'left', title_xref = 'paper', 
                    title_font=dict(family="Arial", size=20), 
                     font=dict(family="Arial", size=14),
                     plot_bgcolor='White',
                     paper_bgcolor = 'White',
                     colorway = cw,
                                    hovermode="x",
                                    hoverdistance=100, # Distance to show hover label of data point
                                    spikedistance=1000, # Distance to show spike
                     xaxis = dict(linecolor = 'black', 
                                    showspikes=True, # Show spike line for X-axis
                                    spikethickness=2,
                                    spikedash="dot",
                                    spikecolor="#999999",
                                    spikemode="across",
                                  showline= True, linewidth= 1, tickangle = 30, ticks='outside', gridcolor='Lavenderblush', ticklabelmode = 'instant', showgrid = True),
                     yaxis = dict(linecolor = 'black', 
                                  showline=True, linewidth = 1, tickangle = 0, gridcolor='Lavenderblush', ticklabelmode = 'instant', showgrid = True),
                     legend = dict(bgcolor = 'whitesmoke', bordercolor = 'grey', borderwidth = 1)
                    )
                        )

## Zemo Choropleth Graph Theme
zemo_template_choro = dict(
    layout=go.Layout(title_font=dict(family="Arial", size=15), 
                     font=dict(family="Arial", size=14),
                     plot_bgcolor='White',
                     paper_bgcolor = 'White',
                     #colorway=px.colors.sequential.Oranges,
                     #basemap_visible = False,
                     margin={'r': 0, 't': 5, 'l': 15, 'b': 0}, 
                     #geo=dict(bgcolor= 'rgba(0,255,255,0.3)')
                        ))
theme_color_scale=["#F8ED94", "#42B029", "#00A8E0", "#001A70"]    


## Style template for div boxes
style_template = {'border': '0px solid #001a70'}

width_template = {"size": 10, "offset": 1}


# # 3. Define App Layout
# 
# This defines the global page layout across all pages. Individual page layout definitions are in later Step 4 onwards.

# ##### 1. Defining toast component for interactivity pop-up

# In[4]:


toast = html.Div(
    [
        dbc.Button(
            "Learn about interactivity",
            id="positioned-toast-toggle",
            color="primary",
            n_clicks=0,
        ),
        dbc.Toast(
            "Interact with charts whenever you hover, click-and-drag, or select points. Double-click items in legend to isolate in chart. Reset changes by clicking home icon on top right of plot. Plots are highly customisable and can be tweaked upon request. They can all be downloaded as png files or embedded via an iframe link.",
            id="positioned-toast",
            header="Interactivity",
            is_open=False,
            dismissable=True,
            icon="danger",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 100, "right": 10, "width": 350},
        ),
    ]
)


@app.callback(
    Output("positioned-toast", "is_open"),
    [Input("positioned-toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False


# ##### 2. Defining navigation bar component

# In[5]:


ZEMO_LOGO = "https://transportandenergy.com/wp-content/uploads/2021/02/ZemoPartnership_Logo.png"

navbar = dbc.Navbar(

        [
    html.A(
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=ZEMO_LOGO, height="100px")),
                dbc.Col(dbc.NavbarBrand('Data Monitoring Portal', class_name="mx-auto g-0 d-flex justify-content-center", style={'font-size':40})),
            ],
            align="center",
            justify = "between"
            #className="g-0",
        ),
        href='/page-content',
    ),

    dbc.Row([
        dbc.Col([
            toast
        ], width =3),
        dbc.Col(
        [dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem('Emissions Data', href='/page-2'),
                    dbc.DropdownMenuItem('Chargepoint Data', href='/page-3'),
                    dbc.DropdownMenuItem('Vehicle Data', href='/page-4'),
                    dbc.DropdownMenuItem('Local Authority Data', href='/page-5'),
                    dbc.DropdownMenuItem('EVET Modelling Data', href='/page-6'),
                    dbc.DropdownMenuItem('Grid Infrastructure Data', href='/page-7'),
                    dbc.DropdownMenuItem('Other Zemo WG Data', href='/page-1'),
                ],
                align_end=True,
                in_navbar=False,
                #direction='start',
                size='lg',
                color="info",
                label="Jump to Data Category",
                        ),
        ], width =3)
            ],     
    className="flex-nowrap mt-3 mt-md-0 me-3 ms-auto",
    align="center")  
        ],
    color="primary",
    dark=True,
    sticky ='top'
    
)


# In[6]:


## Future potential for live updating app
# def serve_layout():
#     return html.H1('The time is: ' + str(datetime.datetime.now()))

# app.layout = serve_layout


# In[7]:


##Initialising app layout

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# # 4. Home page layout

# In[8]:


index_page = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
    dcc.Markdown('''   
    ### Welcome to the Data Monitoring portal (Beta) 
    created, maintained and provided by [Zemo Partnership&apos;s Energy Infrastructure Working Group](https://www.zemo.org.uk/work-with-us/energy-infrastructure/working-group.htm)
                 ''')], 
                style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
               'backgroundColor':'#FFFFFF',
               'border': 'thin lightgrey dashed', 
                               'padding': '6px 0px 0px 8px'}),
            html.Div([
    dcc.Markdown('''
    This web application provides a centralised repository for interactive data visualisations that monitor the electrification of transport and energy in the UK, as well as transparent and easy access to all the data sources used.

    Built with Python, Dash, and deployed via HerokuApp, this application provides EIWG members with an in-depth look at the key indicators within the seven categories below. 

    Questions, comments, or concerns? Feel free to reach out at meziane.benmaamar@zemo.org.uk!

    NOTE: This app optimized for desktop use - A mobile layout will be released in the future.

    _Last updated: September 30th, 2022_
                 ''')
            ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
               'backgroundColor':'#FFFFFF',
               'border': 'thin lightgrey dashed', 
                               'padding': '6px 0px 0px 8px'})
                ], width = 7),

    ]),
    html.Div([
    dbc.Row([
    dbc.ButtonGroup([
        dbc.Button('Emissions Data', href='/page-2', color="info", className="me-1"),    
        dbc.Button('Chargepoint Data', href='/page-3', color="info", className="me-1"),
        dbc.Button('Vehicle Data', href='/page-4', color="info", className="me-1"),
        dbc.Button('Local Authority Data', href='/page-5', color="info", className="me-1"),
        dbc.Button('EVET Modelling Data', href='/page-6', color="info", className="me-1"),
        dbc.Button('Grid Infrastructure Data', href='/page-7', color="info", className="me-1"),
        dbc.Button('Other Zemo WG Data', href='/page-1', color="dark", className="me-1")
                    ]),  
            ], className="g-0", justify = 'center',) 
                    ]),
    html.Div([
    dbc.Row([
        dbc.Col(
            html.Div([
            html.Iframe(src="https://www.zemo.org.uk/",
            style={"height": "800px", "width": "100%", "max-width": "none"}),
                    ], style= {'width': 'max'}), width='12'
                )
            ]) 
                ])

]),


# # 5. All Data & Visualisations
# 
# This section processes data and visualisations across the active pages.
# 
# 1. Other Zemo WG Data
# 2. Emissions Data
# 3. Chargepoint Data
# 4. Vehicle Data
# 5. Local Authority Data
# 6. EVET Modelling Data**
# 7. Grid Infrastructure Data**
# 
# ** These data is handled separately in Section 5 (Page Layout Definitions) tentatively as data is still stored in Plotly Studio (i.e. referenced via iframes rather than direct processing here). To be transferred via code.

# ## Other Zemo WG Data - Key Indicator

# In[9]:


df = pd.read_csv('mass-energy-af-v2.csv')

#line of best fit modelling

dfdropna = df.dropna()

x = sm.add_constant(dfdropna['MIRO (kg)'])
model = sm.OLS(dfdropna['Z (Wh/km)'], x).fit()
dfdropna['bestfit']=model.fittedvalues


dfdropna['weightedMIRO'] = dfdropna['MIRO (kg)']*dfdropna['Number']


wAVG = dfdropna['weightedMIRO'].sum() / dfdropna['Number'].sum()

print("Median MIRO (kg):", dfdropna['MIRO (kg)'].median(),
      ", Weighted average (kg):", wAVG)


# ### Bubble, 3d and box plots for mass vs energy

# In[10]:


fig3dpx = px.scatter_3d(df, x='MIRO (kg)', y='Z (Wh/km)', z='Number',
              color='Fuel',
              title = 'Volume of model fleet on third axis', 
              #size = 'Number',
              symbol='Fuel', opacity=1)

#fig3dpx.update_layout(autosize=False, width=500,height=500)

##box plots
x = 'Z (Wh/km)'
y = 'MIRO (kg)'

a = df.query('Fuel== "PLUG-IN HYBRID ELECTRIC"')[x]
b = df.query('Fuel == "ELECTRICITY"')[x]
c = df.query('Fuel == "PLUG-IN ELECTRIC DIESEL"')[x]
d = df.query('Fuel == "EREVS"')[x]


data = [go.Box(y=a, name = 'Plug-in Hybrid Electric'), go.Box(y=b, name = 'EV'), go.Box(y=c, name='Plug-in Electric Diesel'), go.Box(y=d, name = 'EREV')]

layout = go.Layout(title = 'Box plot distributions for the Z (Wh/km) for different fuels',
                   yaxis = dict(title='Z (Wh/km)'),
                   xaxis = dict(title='Fuel'),
                  template = zemo_template_spike)


boxfig = go.Figure(data=data, layout=layout)

a1 = df.query('Fuel== "PLUG-IN HYBRID ELECTRIC"')[y]
b1 = df.query('Fuel == "ELECTRICITY"')[y]
c1 = df.query('Fuel == "PLUG-IN ELECTRIC DIESEL"')[y]
d1 = df.query('Fuel == "EREVS"')[y]


data = [go.Box(y=a1, name = 'Plug-in Hybrid Electric'), go.Box(y=b1, name = 'EV'), go.Box(y=c1, name='Plug-in Electric Diesel'), go.Box(y=d1, name = 'EREV')]

layout = go.Layout(title = 'Box plot distributions for the MIRO (kg) for different fuels',
                   yaxis = dict(title='MIRO (kg)'),
                   xaxis = dict(title='Fuel'), 
                   hovermode="x unified",
                   template = zemo_template_spike)


boxmassfig = go.Figure(data=data, layout=layout)


# In[11]:


transportusage = pd.read_csv('COVID19data_11_2022.csv')
date_format_TU = '%d-%b-%Y'
transportusage['Date'] = pd.to_datetime(transportusage['Date'], format = date_format_TU)
transportusage.iloc[:,1:] = transportusage.iloc[:,1:].multiply(100)


# In[12]:


transportusage.columns


# In[13]:


COVIDTUmode_options = ['Cars', 'Light Commercial Vehicles', 'Heavy Goods Vehicles', 'National Rail', 'Transport for London Tube', 'Transport for London Bus', 'Bus (excluding London)', 'Cycling']


# ## Emissions Data - Key Indicator

# ### Sub-sector stacked bar chart

# In[14]:


totEdata = pd.read_csv('totalemissions.csv')

totElist = totEdata.columns.values.tolist()
totElist = totElist[1:]
len(totElist)


layout = go.Layout()    
transportemissions = go.Figure(layout=layout)


transportemissions.add_trace(go.Line(x=totEdata['Year'], y=totEdata[totElist[0]], name=totElist[0]))

for sector in totElist[1:]:
    transportemissions.add_trace(go.Bar(x=totEdata['Year'], y=totEdata[sector], name=sector))

transportemissions.update_yaxes(rangemode="tozero", title = 'MTCO<sub>2e</sub>')

transportemissions.update_layout(barmode = 'stack', template = zemo_template, title = 'Greenhouse gas emissions within transport sub-sectors, UK 1990-2020 (MtCO2e) (Source: <a href="https://www.gov.uk/government/statistics/final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020">BEIS, 2020</a>)')


# ### Sector subplots

# In[15]:


emissions = pd.read_csv('subsector_emissions.csv')


emissionsplot = go.Figure()

emissionsplot = make_subplots(specs=[[{"secondary_y": True}]])

emissionsplot = make_subplots(rows = 2, cols = 2, subplot_titles=("Transport", "Residential", "Business", "Energy Supply"), print_grid=True)
             
emissionsplot.add_trace(go.Bar(x=emissions['Year'], y=emissions['Transport'], 
               name='Transport'), row=1, col=1)

emissionsplot.add_trace(go.Bar(x=emissions['Year'], y=emissions['Residential'], 
               name='Residential'), row=1, col=2)
emissionsplot.add_trace(go.Bar(x=emissions['Year'], y=emissions['Energy Supply'], 
               name='Energy Supply'), row=2, col=2)
emissionsplot.add_trace(go.Bar(x=emissions['Year'], y=emissions['Business'], 
               name='Business'), row=2, col=1)

emissionsplot.update_xaxes(rangemode="tozero", row=1, col=1&2)

emissionsplot.update_yaxes(title = 'MTCO<sub>2</sub>')

emissionsplot.update_layout(title = 'Territorial Carbon dioxide emissions by sector, UK 1990-2021 (MtCO<sub>2</sub>) (Source: <a href="https://www.gov.uk/government/statistics/provisional-uk-greenhouse-gas-emissions-national-statistics-2021">BEIS, 2021</a>)<br><sup>Top four most emitting sectors. 2021 data is provisional.</sup>', template = zemo_template_spike)


# ## Chargepoint Data - Key Indicator

# In[16]:


ZapMapPUB = pd.read_csv('ZapMapPUBCP.csv')

ZapMapPUB = ZapMapPUB.rename (columns = {'Unnamed: 0':'Year'}) 
ZapMapPUBx = ZapMapPUB[['slow', 'fast', 'Rapid', 'Ultra - Rapid', 'Total', 'Forecast']].replace(',', '', regex=True).astype(float)

ZapMapPUBx = ZapMapPUBx.join(ZapMapPUB['Year'])


# ### Various chargepoint and connector mixed charts

# In[17]:


layout = go.Layout()
ZapMapfig = go.Figure(layout=layout)

#ZapMapPUB['Rapid Devices'] = pd.to_numeric(ZapMapPUB['Rapid Devices'],errors='coerce')
#ZapMapPUB['Total  Devices'] = pd.to_numeric(ZapMapPUB['Total  Devices'],errors='coerce')


ZapMapfig.add_trace(go.Bar(x=ZapMapPUBx['Year'], y=ZapMapPUBx['slow'].dropna().astype(int), 
               name="Slow Devices (3-5kW)"))
ZapMapfig.add_trace(go.Bar(x=ZapMapPUBx['Year'], y=ZapMapPUBx['fast'].dropna().astype(int), 
               name="Fast Devices (7-22kW)"))  
ZapMapfig.add_trace(go.Bar(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Rapid'].dropna().astype(int), 
               name="Rapid Devices (25-99kW)"))  
ZapMapfig.add_trace(go.Bar(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Ultra - Rapid'].dropna().astype(int), 
               name="Ultra-Rapid Devices (100kW+)"))  

ZapMapfig.add_trace(go.Line(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Total'].dropna().astype(int)
             , name="Total Chargepoint Devices"))

ZapMapfig.update_layout(template = zemo_template_spike, title = 'U.K Public Chargepoints Numbers (Source: <a href="https://www.zap-map.com/statistics/#points">ZapMap, September 2022</a>)')

#ZapMapfig.update_layout(font=dict(family="Calibri", size=24), title = "U.K Public Chargepoints Numbers (Source: ZapMap)")


# In[18]:


rslt_df5 = pd.read_csv('EVHS-WCSdata.csv')
EVHSdevices = rslt_df5['Charging Devices Installed'].replace(',', '', regex=True).astype(float)
pd.to_numeric(EVHSdevices)


layout = go.Layout(
)
UKprivateCP = go.Figure(layout=layout)
#UKprivateCP.update_layout(xaxis=dict(
#    rangeselector=dict(
#            buttons=list([
#                dict(count=1, label="1m", step="month", stepmode="backward"),
#                dict(count=6, label="6m", step="month", stepmode="backward"),
#                dict(count=1, label="YTD", step="year", stepmode="todate"),
#                dict(count=1, label="1y", step="year", stepmode="backward"),
#                dict(step="all")])),
#    rangeslider=dict(visible=True),
#    type="date"
#))



UKprivateCP.add_trace(go.Bar(x=rslt_df5['Date'], y=rslt_df5['Sockets installed'].fillna(0).astype(int).cumsum(),name="WCS Sockets installed"))                 

UKprivateCP.add_trace(go.Bar(x=rslt_df5['Date'], y=EVHSdevices.head(-1).cumsum(), name="EVHS Charging Devices Installed"))


UKprivateCP.update_yaxes(rangemode="tozero")
UKprivateCP.update_layout(barmode = 'stack')

UKprivateCP.update_layout(template = zemo_template_spike, title = 'U.K Private Chargepoints installed via EVHS and WCS grants (Source: <a href="https://www.gov.uk/government/statistics/electric-vehicle-charging-device-grant-scheme-statistics-january-2022/electric-vehicle-charging-device-grant-scheme-statistics-january-2022#annex-a-evhs-and-wcs-regional-table">DfT, July 2022</a>)')


# In[19]:


connectionTypes = pd.read_csv('connectionTypes.csv')

layout = go.Layout()

connectorType = go.Figure(layout=layout)

connectorType.add_trace(go.Bar(x=connectionTypes['Year'], y=connectionTypes['CHAdeMO'], 
               name="CHAdeMO"))                 

connectorType.add_trace(go.Bar(x=connectionTypes['Year'], y=connectionTypes['CCS']
             , name="CCS"))

connectorType.add_trace(go.Bar(x=connectionTypes['Year'], y=connectionTypes['Type 2']
             , name="Type 2"))

connectorType.add_trace(go.Bar(x=connectionTypes['Year'], y=connectionTypes['Tesla (type 2 & CC)']
             , name="Tesla (type 2 & CC)"))


connectorType.update_yaxes(rangemode="tozero")

connectorType.update_layout(template=zemo_template_spike, title = 'U.K Public Rapid Chargepoints Numbers by connection type (Source: <a href="https://www.zap-map.com/statistics/#points">ZapMap, September 2022</a>)')


# ## Vehicle Data - Key Indicator

# ### Unused SMMT site data

# In[20]:


SMMT = pd.read_csv('SMMTcsv.csv')

SMMT['Type']=SMMT['Type'].astype(int)

print(SMMT.dtypes)

layout = go.Layout(
        #margin=go.Margin(l=100),
       )
vehicleplot = go.Figure(layout=layout)

vehicleplot = make_subplots(specs=[[{"secondary_y": True}]])
    
#vehicleplot.add_trace(go.Line(x = SMMT['Year'].iloc[18:48], 
#                                     y = SMMT['Grand Total'].iloc[18:31].cumsum(), name="Total Cumulative Greenhouse gas emissions, UK 2008-2020 (MtCO2e)"))                
             
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['Diesel'], name="Diesel"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['Petrol'], name="Petrol"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['BEV'], name="BEV"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['PHEV'], name="PHEV"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['HEV'], name="HEV"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['MHEV (Diesel)'], name="MHEV (Diesel)"))
vehicleplot.add_trace(go.Bar(x = SMMT['Type'], 
                                     y = SMMT['MHEV (Petrol)'], name="MHEV (Petrol)"))



vehicleplot.add_trace(go.Line(x = SMMT['Type'], 
                                     y = SMMT['BEV Market Share']*100, name="BEV Market Share"), secondary_y = True)
vehicleplot.add_trace(go.Line(x = SMMT['Type'], 
                                     y = SMMT['PHEV Market Share']*100, name="PHEV Market Share"), secondary_y = True)


#vehicleplot.add_trace(go.Line(x = SMMT['Year'], y = SMMT['Grand Total'], name="Total Cumulative Greenhouse gas emissions, UK 2008-2020 (MtCO2e)"))                
#vehicleplot.add_trace(go.Bar(x = SMMT['Year'], y = SMMT['Carbon Budget Target'], name="Carbon-Budgets Targets"), secondary_y = True)               

vehicleplot.update_layout(barmode = 'stack')

vehicleplot.update_yaxes(rangemode="tozero", ticksuffix = '%', secondary_y = True)

vehicleplot.update_layout(template = zemo_template_spike, xaxis={'tickformat': ',d'},  title = "SMMT data, Source: SMMT, 2021")


# ### Vehicle parc and sales data

# In[21]:


## Converting vehicle data to datetime format to allow for rangeslider and buttons

vehicleparc = pd.read_csv('parc_Q2_2022.csv')

date_format_1 = '%B %Y'
date_format_2 = '%Y %B'

monthlysales = vehicleparc[vehicleparc['Chart_type']=='Sales (Monthly)']
monthlysales['Period'] = pd.to_datetime(monthlysales['Period'], format = date_format_1)

quarterlysales = vehicleparc[vehicleparc['Chart_type']=='Sales (Quarterly)']
quarterlysales['Period'] = pd.to_datetime(quarterlysales['Period'], format = date_format_2)

quarterlyparc = vehicleparc[vehicleparc['Chart_type']=='Parc']
quarterlyparc['Period'] = pd.to_datetime(quarterlyparc['Period'], format = date_format_2)


vehicleparc_dt1 = monthlysales.append(quarterlysales)

vehicleparc_dt = vehicleparc_dt1.append(quarterlyparc)


# In[22]:


##Defining lists to be used in the drop down options in page_x_layout dcc.dropdown

vehicle_types_parc = ['Bus', 'Car', 'HGV', 'Van', 'Motorcycle', 'Other']
chart_type = ['Parc', 'Sales (Quarterly)', 'Sales (Monthly)']
chart_type2 = ['Parc', 'Sales (Quarterly)']

hc_chart_type = ['Receipts', 'Quantities']

vehicle_type_veh156 = ['Cars','Light goods vehicles'] 


# ### Hydrocarbon bulletin data for receipts and volumes

# In[23]:


##Convering data to datetime format

hcbulletin = pd.read_csv('hc_oils_bulletin_q2_2022.csv')

hcbulletin.iloc[:,1:16].replace(',', '', regex=True).astype(float)

date_format_1 = '%B %Y'

hcbulletin['Period'] = pd.to_datetime(hcbulletin['Period'], format = date_format_1)

hcbulletinlist = hcbulletin.columns.values.tolist()
bar_hcbulletinlist_1 = np.append(hcbulletinlist[1:7], hcbulletinlist[8:12]) 
bar_hcbulletinlist = np.append(bar_hcbulletinlist_1 , hcbulletinlist[13:15])

line_hcbulletinlist_1 = np.append(hcbulletinlist[7], hcbulletinlist[12])
line_hcbulletinlist = np.append(line_hcbulletinlist_1, hcbulletinlist[15])


#hcbulletin
#vehicleparc_dt1 = monthlysales.append(quarterlysales)


# ### WLTP CO2 Emissions of vehicles registered data

# In[24]:


veh156 = pd.read_csv('veh156_Q2_2022.csv')

date_format_x = '%B %Y'

veh156['Date'] = pd.to_datetime(veh156['Date'], format = date_format_x)

veh156list = veh156.columns.values.tolist()
string = ' (WLTP)'
veh156list_wltp = [x + string for x in veh156list]

veh156list = veh156list[7:12]

veh156list_LGV = np.append(veh156list[0:2], veh156list[4])

veh156list_LGV


# ## Local Authority Data - Key Indicator

# In[25]:


with open('Local_Authority_Districts_(December_2021)_GB_BUC.geojson') as g:
    LA_map2 = json.load(g)

LAem = pd.read_csv('uk-local-authority-ghg-emissions-2020-dataset.csv')


# In[26]:


LAdf = pd.read_csv ('LACPpercapita_2022_q2.csv')
with open('Local_Planning_Authorities_(May_2021)_UK_BUC.geojson') as f:
    LA_map = json.load(f)

LAnames = list(LAdf.name)
geojson_LAnames = sorted([str(LA_map['features'][i]['properties']['LPA21NM']) for i in range(len(LA_map['features']))])

print(len((set(LAnames) ^ set(geojson_LAnames))))


LAdf = LAdf.rename(columns = {'percapita':'Chargepoints per 100k people'})
LAdf = LAdf.rename(columns = {'percapita (excl. London)':'Chargepoints per 100k people (excl. London)'})
LAdf = LAdf.rename(columns = {'number':'Total Number of Public Chargepoints'})
LAdf = LAdf.rename(columns = {'rdpercapita':'Rapid Chargepoints per 100k people'})
LAdf = LAdf.rename(columns = {'number rd':'Total Number of Rapid Public Chargepoints'})
LAdf = LAdf.rename(columns = {'Recent quarterly growth rate (%)':'January-April Quarterly growth rate (%)'})



#df['Average quarterly growth rate (%)'] = df['Average quarterly growth rate (%)'].astype(float)
LAdf.round(2)

LAdf.drop(columns= LAdf.columns[-8:], axis=1, inplace=True)

LAdf['Local Planning Authority'] = LAdf['name'].str.replace(r' LPA$', '')    


# In[27]:


# Defining dropdown labels
sector_options = []

for sector in LAem['LA GHG Sub-sector'].unique():
    sector_options.append({'label': str(sector), 'value': sector})
    
region_options = []

for region in LAem['Region'].unique():
    region_options.append({'label': str(region), 'value': region})
'''  
region_options2 = []
for region2 in LAdf['Region'].unique():
    region_options2.append({'label': str(region2), 'value': region2})

cpstats_options = [{'label':'Chargepoints per 100k people' , 'value2':'Chargepoints per 100k people'}, 
                   {'label':'Chargepoints per 100k people (excl. London)' , 'value2':'Chargepoints per 100k people (excl. London)'}, 
                   {'label':'Total Number of Public Chargepoints' , 'value2':'Total Number of Public Chargepoints'}, 
                   {'label':'Rapid Chargepoints per 100k people' , 'value2':'Rapid Chargepoints per 100k people'}, 
                   {'label':'Total Number of Rapid Public Chargepoints' , 'value2':'Total Number of Rapid Public Chargepoints'}, 
                   {'label':'Recent quarterly growth rate (%)', 'value2':'Recent quarterly growth rate (%)'},
                   {'label':'January-April Quarterly growth rate (%)', 'value2':'January-April Quarterly growth rate (%)'}]
'''  


# In[28]:


# Defining dropdown text in app layout
markdown_text = '''### 
The UK produces a breakdown of greenhouse gas emissions by Local Authority area as a subset of its annual inventory of greenhouse gas emissions. 
The main data sources are the UK National Atmospheric Emissions Inventory and the BEIS National Statistics of energy consumption for local authority areas.
Those emissions excluded are aviation, shipping and military transport for which there is no obvious basis for allocation to local areas.
'''

markdown_subtext = '''###
The nationally available data sets for GHG begin in 2005. 
- Prior to this period, the publication statistics covered emissions of carbon dioxide only. 
- Shown here is the most recent data for the year __2020__ (last updated in June 2022).
'''


# ### Creating choropleth graphs for LA data

# In[29]:


fig1 = px.choropleth(LAdf, geojson=LA_map2, 
                    color="Total Number of Public Chargepoints",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator",
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Total Number of Public Chargepoints'], 
                    #template = 'ggplot2', 
                    basemap_visible = True,
                    range_color = [1, 400],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Total number of Public chargepoints', 
                  # height = 620, width = 900
                    )
fig1.update_geos(fitbounds="geojson", visible=False)
fig1.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
fig1.update_coloraxes(colorbar_title_text="Number of public chargepoints", colorbar_tickprefix = ">", colorbar_showtickprefix = "last", colorbar_title_side = "right")

#fig1.layout.font.family = 'Poppins'


# In[30]:


fig2 = px.choropleth(LAdf, geojson=LA_map2, color="Total Number of Rapid Public Chargepoints",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Total Number of Rapid Public Chargepoints'], 
                    #template = 'ggplot2', 
                    basemap_visible = True,
                    #range_color = [1, 401],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Total number of Rapid Public chargepoints', 
                    #height = 620, width = 900
                    )
fig2.update_geos(fitbounds="geojson", visible=False)
fig2.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
fig2.update_coloraxes(colorbar_title_text="Number of rapid public chargepoints", colorbar_title_side = "right")
#fig2.layout.font.family = 'Poppins'


# In[31]:


fig3 = px.choropleth(LAdf, geojson=LA_map2, color="Chargepoints per 100k people (excl. London)",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Chargepoints per 100k people (excl. London)'], 
                    template = 'ggplot2', 
                    basemap_visible = True,
                    #range_color = [1, 401],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Public chargepoints per 100k people (excl. London)', 
                    #height = 620, width = 900
                    )
fig3.update_geos(fitbounds="geojson", visible=False)
fig3.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
fig3.update_coloraxes(colorbar_title_text="Number of public chargepoints", colorbar_title_side = "right")

#fig3.layout.font.family = 'Poppins'


# In[32]:


fig4 = px.choropleth(LAdf, geojson=LA_map2, color="Chargepoints per 100k people",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Chargepoints per 100k people'], 
                    template = 'ggplot2', 
                    basemap_visible = True,
                    range_color = [1, 500],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Public chargepoints per 100k people', 
                    #height = 620, width = 900
                    )
fig4.update_geos(fitbounds="geojson", visible=False)
fig4.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
fig4.update_coloraxes(colorbar_title_text="Number of public chargepoints", colorbar_tickprefix = ">", colorbar_showtickprefix = "last", colorbar_title_side = "right")
fig4.show()

#fig4.layout.font.family = 'Poppins'


# In[33]:


fig5 = px.choropleth(LAdf, geojson=LA_map2, color="Rapid Chargepoints per 100k people",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Rapid Chargepoints per 100k people'], 
                    template = 'ggplot2', 
                    basemap_visible = True,
                    #range_color = [1, 401],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Rapid Public chargepoints per 100k people', 
                    #height = 620, width = 900
                    )
fig5.update_geos(fitbounds="geojson", visible=False)
fig5.update_coloraxes(colorbar_title_text="Number of rapid public chargepoints", colorbar_title_side = "right")
fig5.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
#fig5.layout.font.family = 'Poppins'


# In[34]:


fig6 = px.choropleth(LAdf, geojson=LA_map2, color="Average yearly growth rate (%)",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale=theme_color_scale, 
                    hover_name = LAdf['Average yearly growth rate (%)'], 
                    template = 'ggplot2', 
                    basemap_visible = True,
                    #range_color = [1, 401],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Average yearly growth rate since October 2019', 
                    #height = 620, width = 900
                    )
fig6.update_geos(fitbounds="geojson", visible=False)
fig6.update_coloraxes(colorbar_title_text="Average yearly growth rate", colorbar_title_side = "right", colorbar_ticksuffix = "%", colorbar_showticksuffix = "all")
fig6.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
#fig6.layout.font.family = 'Poppins'


# In[35]:


fig7 = px.choropleth(LAdf, geojson=LA_map2, color="January-April Quarterly growth rate (%)",
                    locations="Local Planning Authority", featureidkey="properties.LAD21NM",
                    projection="mercator", 
                    color_continuous_scale="thermal_r", 
                    hover_name = LAdf['January-April Quarterly growth rate (%)'], 
                    template = 'ggplot2', 
                    basemap_visible = True,
                    #range_color = [0,50],
                    #color_discrete_map = {"missingdata":"#000000"},
                    title = 'Average quarterly growth rate since October 2019', 
                    #height = 620, width = 900
                    )
fig7.update_geos(fitbounds="geojson", visible=False)
fig7.update_coloraxes(colorbar_title_text="Average quarterly growth rate", colorbar_title_side = "right", colorbar_ticksuffix = "%", colorbar_showticksuffix = "all")
fig7.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
#fig7.layout.font.family = 'Poppins'


# In[36]:


## Defining list of dropdown values for LA region dcc.dropdown option below

valueLAdata = LAem['Region'].unique()
pcvalueLAdata = valueLAdata.tolist()
pcvalueLAdata


# ## EVET Modelling Data - Key Indicator

# ### EVET parc sales pie chart

# In[37]:


ESCpub = pd.read_csv('ESC_cp_numbers.csv')
ESCpri = pd.read_csv('ESC_home_cp.csv')
ESCparc = pd.read_csv('ESC_vehicle_parc.csv')
ESCparc = ESCparc.T
ESCsales = pd.read_csv('ESC_propofsales_powertrain.csv')
ESCnewsales = pd.read_csv('ESC_new_sales_powertrain.csv')


pielabels = ESCparc.iloc[: , 1:].columns.tolist()

ESCparc.columns = ESCparc.iloc[0].astype(str)
ESCparc = ESCparc.iloc[1: , :]

ESCparc.index


# In[38]:


SMMT_data = [18350000, 13500000, 3150000, 0]

ESCparc['SMMT'] = SMMT_data


# In[39]:


ESCsales.iloc[:,1:-1] = ESCsales.iloc[:,1:-1].multiply(100)


# In[40]:


ESCyearproj = ESCpub['Year'].iloc[2:].tolist()

ESCpubheader  = ESCpub.columns.tolist()

ESCpub['Year'] = ESCpub['Year'].astype(str)
ESCyearproj = ESCpub['Year'].iloc[2:].astype(str)
ZapMapPUBx['growthrate'] = ZapMapPUBx['Total'].pct_change()


# In[41]:


# Create subplots: use 'domain' type for Pie subplot
ESCparcfig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
ESCparcfig.add_trace(go.Pie(labels=ESCparc.index, values=ESCparc['2030.0'], name="2030"),
              1, 1)
ESCparcfig.add_trace(go.Pie(labels=ESCparc.index, values=ESCparc['2035.0'], name="2035"),
              1, 2)

# Use `hole` to create a donut-like pie chart
ESCparcfig.update_traces(hole=.4, hoverinfo="label+value+name")

ESCparcfig.update_layout(template = zemo_template,
    title_text="Vehicle parc split by powertrain, EVET central case modelling",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='2030', x=0.19, y=0.5, font_size=20, showarrow=False),
                 dict(text='2035', x=0.81, y=0.5, font_size=20, showarrow=False)])
#ESCparcfig.show()


# ## Grid Infrastructure Data - Key Indicator

# ### WPD LCT data

# In[42]:


#an API may be possible here check out the new NGED portal

WPDLCTconnections = pd.read_csv('lct_con-4.csv')
WPDLCTenquiries = pd.read_csv('lct_enq-4.csv')

WPDLCTconnections['date'] = pd.to_datetime(WPDLCTconnections['date'], dayfirst = True)
WPDLCTconnections.sort_values(['date'], ascending=[False])



WPDLCTconnections['month_date'] = WPDLCTconnections['date'].dt.strftime('%b-%Y')
WPDLCTconnections['month_date']
#WPDLCTconnections = WPDLCTconnections.rename(columns = {'group_date':'Date'})


wpd_LCT = WPDLCTconnections.groupby(['date']).sum()

wpd_LCT.sort_values(['date'], ascending=[True])

wpd_LCT.reset_index(inplace=True)

WPDLCTenquiries['date'] = pd.to_datetime(WPDLCTenquiries['date'], dayfirst = True)
WPDLCTenquiries.sort_values(['date'], ascending=[False])



WPDLCTenquiries['month_date'] = WPDLCTenquiries['date'].dt.strftime('%b-%Y')
WPDLCTenquiries['month_date']
#WPDLCTenquiries = WPDLCTenquiries.rename(columns = {'group_date':'Date'})


wpd_LCT_enq = WPDLCTenquiries.groupby(['date']).sum()

wpd_LCT_enq.sort_values(['date'], ascending=[True])

wpd_LCT_enq.reset_index(inplace=True)

#wpd_LCT
WPDLCTenquiries['month_date']

layout = go.Layout()

wpdLCTconnections = go.Figure(layout=layout)


wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT['date'], y=wpd_LCT['EV'].cumsum(), name="Electric Vehicle chargepoint"))
wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT_enq['date'], y=wpd_LCT_enq['EV'].cumsum(), name="Electric Vehicle chargepoint enquiries", line=dict(width=2, dash = 'dash')))                 

wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT['date'], y=wpd_LCT['HP'].cumsum(), name="Heat pump", visible='legendonly'))
wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT_enq['date'], y=wpd_LCT_enq['HP'].cumsum(), name="Heat pump enquiries", line=dict(width=2, dash = 'dash'), visible='legendonly'))


wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT['date'], y=wpd_LCT['PV'].cumsum(), name="PV generation", visible='legendonly'))
wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT_enq['date'], y=wpd_LCT_enq['PV'].cumsum(), name="PV generation enquiries", line=dict(width=2, dash = 'dash'), visible='legendonly'))

wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT['date'], y=wpd_LCT['ES'].cumsum(), name="Storage", visible='legendonly'))
wpdLCTconnections.add_trace(go.Scatter(x=wpd_LCT_enq['date'], y=wpd_LCT_enq['ES'].cumsum(), name="Storage enquiries", line=dict(width=2, dash = 'dash'), visible='legendonly'))


wpdLCTconnections.update_yaxes(rangemode="tozero", title = "Number of LCT connections and enquiries")

wpdLCTconnections.update_layout(template=zemo_template_spike, title = 'Number of connections per low carbon technology (LCT) on WPD networks from April 2017 to October 2022 (Source: <a href="https://connecteddata.westernpower.co.uk/dataset/lct-enquiries">NGED Connected Data Portal, October 2022</a>)')


#py.plot(wpdLCTconnections, filename = 'wpdLCTconnections', auto_open = False)


# In[43]:


#List for dcc.dropdown component in the layout 
selected_connection_list = ['Budget Estimates Provided', 'Connection Offer Accepted', 'Connection Offer Not Accepted']


# ### WPD Capacity data

# In[44]:


WPDcapacity = pd.read_csv('new-connections-may-2022-update.csv')

WPDcapacity = WPDcapacity.sort_values(by ='Connection Status')

WPDcapacity['Proposed Connection Voltage (kV)'] = WPDcapacity['Proposed Connection Voltage (kV)'].astype(str)


WPDcapacity_list = WPDcapacity['Connection Status'].unique()


WPDcapacity2021 = WPDcapacity[WPDcapacity['year']==2021]
WPDcapacity2022 = WPDcapacity[WPDcapacity['year']==2022]



WPDcapacity2021_BEP = WPDcapacity2021[WPDcapacity2021['Connection Status']== 'Budget Estimates Provided']
WPDcapacity2022_BEP = WPDcapacity2022[WPDcapacity2022['Connection Status']== 'Budget Estimates Provided']

WPDcapacity2021_COA = WPDcapacity2021[WPDcapacity2021['Connection Status']== 'Connection Offer Accepted']
WPDcapacity2022_COA = WPDcapacity2022[WPDcapacity2022['Connection Status']== 'Connection Offer Accepted']

WPDcapacity2021_CNA = WPDcapacity2021[WPDcapacity2021['Connection Status']== 'Connection Offer Not Accepted']
WPDcapacity2022_CNA = WPDcapacity2022[WPDcapacity2022['Connection Status']== 'Connection Offer Not Accepted']


#WPDcapacity2022 = WPDcapacity[WPDcapacity['year']==2022]
WPDcapacity2021_BEP

WPDindicator_list = WPDcapacity.columns[6:10].values.tolist()

WPDindicator_list[3]


# ### Interactive WPD capacity visualisation

# In[45]:


# List for dcc.dropdown element in page layout 

WPDindicator_list = WPDcapacity.columns
WPDindicator_list = WPDindicator_list[6:10]

WPDindicator_list


# ### ENA Flexibility market data

# In[46]:


rslt_df8 = pd.read_csv('flexfigures_2022-23.csv')

layout = go.Layout(
        #height = 620, width = 750,
        #margin=go.Margin(l=100),
       )

industryflex = go.Figure(layout=layout)

industryflex = make_subplots(specs=[[{"secondary_y": True}]])

industryflex.add_trace(go.Bar(x=rslt_df8['Period'], y=rslt_df8['Sustain (MW)'],name="Sustain (MW)"))
industryflex.add_trace(go.Bar(x=rslt_df8['Period'], y=rslt_df8['Secure (MW)'], name="Secure (MW)"))
industryflex.add_trace(go.Bar(x=rslt_df8['Period'], y=rslt_df8['Restore (MW)'], name="Restore (MW)"))
industryflex.add_trace(go.Bar(x=rslt_df8['Period'], y=rslt_df8['Dynamic (MW)'], name="Dynamic (MW)"))
industryflex.add_trace(go.Bar(x=rslt_df8['Period'], y=rslt_df8['Reactive Power (MVAr)'], name="Reactive Power (MVAr)"))

# Change the bar mode
industryflex.update_layout(barmode='stack')


industryflex.add_trace(
     go.Scatter(mode='markers', marker_color='black', marker_symbol='x', x=rslt_df8['Period'], 
                y=rslt_df8['Percentage of Total Tendered'], name="Percentage of Total Tendered (%)"),
    secondary_y=True)

industryflex.update_yaxes(ticksuffix = "", 
        title_text='Units of Flexibility (MW or MVar)', 
        tickangle = 0,
        title_font_size=18, 
        color = 'rgb(82, 82, 82)',
        #gridcolor='#444',
        ticklabelmode = 'instant', secondary_y=False )

industryflex.update_yaxes(range=[0, 100], 
            ticksuffix = "%", 
            title = "Percentage of Tendered",
            color = '#444',
            secondary_y = True)
industryflex.update_layout(xaxis = dict(
        showline=True,
        showgrid=True,
        showticklabels=True,
        linewidth=1,
        ticks='outside',
        tickfont=dict(
            #family='Poppins',
            size=12,
            color='#444'),
      ),
    
        yaxis = dict(
        showline=True,
        showgrid=True,
        showticklabels=True,
        linewidth=1,
        ticks='outside',
        tickfont=dict(
            #family='Poppins',
            size=12,
            color='#444',)
        ),
            
        plot_bgcolor='White'
                 )

industryflex.update_yaxes(rangemode="tozero")

industryflex.update_layout(template = zemo_template, title = 'Historic DNO Flexibility Contracted/Tendered (Source: <a href="https://www.energynetworks.org/industry-hub/resource-library/?search=ON22-WS1A-P0+Flexibility+Figures+2022%2F23&id=267">ENA 2022</a>)<br><sup>Change in reporting period reflects alignment with Ofgem SLC 31E- Flexibility statements reporting cycle</sup>')


# ### Smart Meter data

# In[47]:


smartmeters = pd.read_csv('smfigures_06_2022.csv')

smartmeters[['Smart in smart mode','Smart in traditional mode','Not-smart']] = smartmeters[['Smart in smart mode', 'Smart in traditional mode', 'Not-smart']].replace(',', '', regex=True).astype(int)
layout = go.Layout(
        #margin=go.Margin(l=100),
        title = " Smart Meter Uptake to date UK")
smplot = go.Figure(layout=layout)

 
smplot.add_trace(go.Bar(x = smartmeters['Quarter'], 
                                     y = smartmeters['Smart in smart mode'], name="Smart in smart mode"))
smplot.add_trace(go.Bar(x = smartmeters['Quarter'], 
                                     y = smartmeters['Smart in traditional mode'], name="Smart in traditional mode"))
smplot.add_trace(go.Bar(x = smartmeters['Quarter'], 
                                     y = smartmeters['Not-smart'], name="Traditional"))

smplot.update_yaxes(title = 'Meters in operation')
smplot.update_layout(template=zemo_template_spike, barmode = 'stack', title = 'U.K Quarterly Domestic electricity meters operated by large energy suppliers (Source: <a href="https://www.gov.uk/government/statistics/smart-meters-in-great-britain-quarterly-update-june-2022">BEIS, 2022</a>)')
#smplot.layout.font.family = 'Poppins'
smplot.show()


# # 5. Page Layout Definitions
# 
# Each cell is page_x_layout
# 
# for x in:
# 1. Other Zemo WG Data
# 2. Emissions Data
# 3. Chargepoint Data
# 4. Vehicle Data
# 5. Local Authority Data
# 6. EVET Modelling Data
# 7. Grid Infrastructure Data

# In[48]:


TU_granularity_options = ['Daily','Weekly']


# In[49]:


@app.callback(Output('transportusage-graph', 'figure'),
              [Input('TU-mode-picker', 'value'), Input('TU-granularity', 'value')])

def update_transportusagefig(TU_selected_mode, TU_granularity):
    
    layout = go.Layout()
    TUfig = go.Figure(layout=layout)
    
    if TU_granularity == 'Daily':
        for modetype in TU_selected_mode:
            TUfig.add_trace(go.Line(x=transportusage['Date'], y=transportusage[modetype], name=modetype)),
        TUfig.update_layout(template = zemo_template_spike, title ='U.K Transport use activity compared to equivalent day pre-COVID-19 pandemic, (Source: <a href="https://www.gov.uk/government/statistics/transport-use-during-the-coronavirus-covid-19-pandemic">DfT, November 2022</a>)'),
    else:
        for modetype in TU_selected_mode:
            TUfig.add_trace(go.Line(x=transportusage['Date'].iloc[::7], y=transportusage[modetype].iloc[::7], name=modetype)),
        TUfig.update_layout(template = zemo_template_spike, title ='U.K Transport use activity compared to equivalent day pre-COVID-19 pandemic, (Source: <a href="https://www.gov.uk/government/statistics/transport-use-during-the-coronavirus-covid-19-pandemic">DfT, November 2022</a>)'),        
    
    TUfig.update_yaxes(title = 'Relative Transport Use Activity', rangemode='tozero', ticksuffix = '%')
    TUfig.update_xaxes(rangeselector = dict(
                buttons=list([
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=2, label="1Y", step="year", stepmode="backward"),                 
                                dict(step="all")])
            ))
    
    return TUfig


# In[50]:


page_1_layout = html.Div([
     navbar,    
     html.H1('Other Zemo WG Data', style={'textAlign': 'center'}),

dbc.Tabs([
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [ 
     dcc.Graph(id='scatterplot2', 
               figure={'data':[
                   go.Scatter(
                           x = df['MIRO (kg)'],
                           y = df['Z (Wh/km)'],
                           name = 'MIRO(kg) vs Z(Wh/km)',
                           mode = 'markers',
                           marker = dict(
                               size= np.log(df['Number']),
                               showscale = False),
                           hovertemplate="%{y}%{_xother}"
                   ),
                   go.Scatter(x=dfdropna['MIRO (kg)'],
                                            y=dfdropna['bestfit'],
                                            hoverlabel=dict(namelength=-1), 
                                            mode='lines',
                                            name='y=0.0888x + 0.0485 <br>(OLS regression best fit)<br> R-squared = 0.64',
                                            line=dict(color='firebrick', width=2, dash = 'dash')
                                           )
                   ], 
                   
                       'layout':go.Layout(
                           title = 'Plug-in cars registered for the first time by fuel type, mass in running order (MIRO),<br><sup> Size of marker is logarithmically proportional to number of vehicles</sup>', 
                           title_x=0,
                           title_font_size = 14,
                           xaxis = {'title':'MIRO (kg)'},
                           yaxis = {'title':'Z (Wh/km)'},
                           template = zemo_template_spike,
                           hovermode="x unified"
                           )}, 
                                responsive = True,
                                style={'width': '95vw'}
               ),
    
              dbc.Row(
                    [
                        dbc.Col(html.Div(dcc.Graph(id = 'scatterplot3',
                        figure={'data':[
                           go.Scatter(
                                   x = df['MIRO (kg)'],
                                   y = df['Z (Wh/km)'],
                                   text = df['Number'],
                                   mode = 'markers',
                                   fill = 'tonext',
                                   marker = dict(
                                       color= (df['Number']),
                                       colorbar=dict(
                                           title="Number of vehicles"),
                                       showscale = True),
                                   hovertemplate="%{y}%{_xother}")
                           ], 

                               'layout':go.Layout(
                                   xaxis = {'title':'MIRO (kg)'},
                                   yaxis = {'title':'Z (Wh/km)'},
                                   template = zemo_template_spike,
                                   hovermode="x unified")},
                         responsive = True,
                         style={'width': '70vw, 20vmin'}
                                                  ),
                        # style={'display': 'inline-block'}
                                        )),
                        dbc.Col(html.Div(dcc.Graph(id = 'px 3d plot',
                         figure = fig3dpx,
                         responsive = True,
                         style={'width': '30vw'}
                                                  ),
                                        )),
                    ], align="center",
                        ),
     dcc.Graph(id = 'energy box plot',
               figure = boxfig,
               #style={'display': 'inline-block'}
               ),
     dcc.Graph(id = 'mass box plot',
               figure = boxmassfig,
               #style={'display': 'inline-block'}
               ),
        ]
                )
                    ), label = 'PCWG visualisations'),
dbc.Tab(dbc.Card(
    dbc.CardBody(
        [
     html.Div([
     dcc.Dropdown(id='TU-mode-picker',
             options = [{'label': x, 'value': x} for x in COVIDTUmode_options],
             value = ['Cars'],
             placeholder='Select transport mode', multi=True),
     dcc.Dropdown(id='TU-granularity',
             options = [{'label': x, 'value': x} for x in TU_granularity_options],
             value = ['Daily']),
    
     dcc.Graph(id = 'transportusage-graph',
               responsive = True
               #style={'display': 'inline-block'}
               ),
         ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                       'padding': '6px 0px 0px 8px'}),
            ]
                )
                    ), label = 'Transport usage statistics')        
])
     ])


# In[51]:


page_2_layout = html.Div([
    navbar,
    html.H1('Emissions Data', style={'textAlign': 'center'}),
    html.Div(id='page-2-content'),
    
    dbc.Row(
            dbc.Col(
                html.Div(dcc.Graph(id = 'transport emissions',
            figure = transportemissions,
            responsive = True 
              #style={'display': 'inline-block'}
            )),
                width= width_template,
            )
        ),
    html.Br(),
    dbc.Row(
            dbc.Col(
                html.Div(dcc.Graph(id = 'sectoral emissions',
             figure = emissionsplot,
             responsive = True
             )),
                width= width_template,
            )
        ),

])


# In[52]:


page_3_layout = html.Div([
    navbar,
    html.H1('Chargepoint Data', style={'textAlign': 'center'}),
    html.Div(id='page-3-content'),
    dcc.Markdown('''
        **Public charging infrastructure across United Kingdom [DfT July 2022 statistics](https://www.gov.uk/government/statistics/electric-vehicle-charging-device-grant-scheme-statistics-july-2022)**      
                '''),
    dbc.Row(dbc.Col(
    html.Div(dcc.Graph(id = 'UKpubCP',
             figure = ZapMapfig,
             #style={'width': '800'},
             responsive = True), 
             #style={'display': 'inline-block'}
            ), width = width_template)),
    dbc.Row(dbc.Col(
    html.Div(dcc.Graph(id = 'UKprivateCP',
             figure = UKprivateCP,
             #style={'width': '800'},
             responsive = True), 
             #style={'display': 'inline-block'}
            ), width = width_template)),
    dbc.Row(dbc.Col(
    html.Div(dcc.Graph(id = 'connectortype',
             figure = connectorType,
             #style={'width': '800'},
             responsive = True), 
            # style={'display': 'inline-block'}
            ), width = width_template)),
], 
#style={'width': '100%', 'display': 'inline-block'}
)


# ### Interactive Vehicle parc and sales visualisation

# In[53]:


@app.callback(Output('vehicleparc-graph', 'figure'),
              [Input('vehicle-picker', 'value'), Input('chart-picker', 'value'), Input('percentage_button', 'value')])

def update_vehicleparcfig(selected_vehicle, selected_chart, percentage_button):
    
    layout = go.Layout()
    vehicleparcfig = go.Figure(layout=layout)   
    
    data = vehicleparc_dt[vehicleparc_dt['Vehicle_type'] == selected_vehicle][vehicleparc_dt['Chart_type']== selected_chart]
    vehicleparclist = vehicleparc.columns.values.tolist()
    fig_list_veh=vehicleparclist[1:12]
    fig_list_veh.reverse()
    
    if percentage_button == 'PX':
        for fueltype in fig_list_veh:
            vehicleparcfig.add_trace(go.Scatter(x=data['Period'], y= 1000 * data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype,
                                    hovertemplate="%{y}%{_xother}",
                                    fill='tonexty', mode = 'none', stackgroup = 'one', groupnorm='percent'             
                                           )),
        vehicleparcfig.update_layout(template=zemo_template),
        vehicleparcfig.update_yaxes(title = 'Percentage of total', ticksuffix = '%')
    else:
        for fueltype in fig_list_veh:
            vehicleparcfig.add_trace(go.Scatter(x=data['Period'], y= 1000 * data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype,
                                    hovertemplate="%{y}%{_xother}",
                                    fill='tonexty', mode = 'none', stackgroup = 'one'          
                                           )),
        vehicleparcfig.add_trace(go.Line(x=data['Period'], y=1000 * data['Total'].replace(',', '', regex=True).astype(float), 
               name="Total")),
        vehicleparcfig.update_layout(template=zemo_template)
        vehicleparcfig.update_yaxes(rangemode = 'tozero', title = 'Number of vehicles')
    
    vehicleparcfig.update_xaxes(
        rangeselector = dict(
                buttons=list([
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=2, label="2Y", step="year", stepmode="backward"),
                                dict(count=4, label="4Y", step="year", stepmode="backward"),                    
                                dict(step="all")])
    ))

    
    vehicleparcfig.update_layout(title = 'Vehicle parc and sales by fuel type (Source: <a href="https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables">DfT, September 2022</a>)')        

    return vehicleparcfig
     


# ### Interactive hydrocarbon bulletin visualisation

# In[54]:


@app.callback(Output('hcbulletin-graph', 'figure'),
              [Input('hc-chart-picker', 'value'), Input('hc_percentage_button', 'value')])

def update_hcbulletinfig(hc_selected_chart, hc_percentage_button):
    
    layout = go.Layout()
    hcbulletinfig = go.Figure(layout=layout)   

    hc_data = hcbulletin[hcbulletin['Chart_type']== hc_selected_chart]

    if hc_percentage_button == 'PX':
        for fueltype in bar_hcbulletinlist:
            hcbulletinfig.add_trace(go.Scatter(x=hc_data['Period'], y=hc_data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype, fill='tonexty', mode = 'none', stackgroup = 'one', groupnorm='percent'          
                                              )),
        hcbulletinfig.add_trace(go.Scatter(x=hc_data['Period'], y=hc_data['Road Fuel gases'].replace(',', '', regex=True).astype(float), 
                                   name='Road Fuel gases', fill='tonexty', mode = 'none', stackgroup = 'one')),
        hcbulletinfig.update_layout(template=zemo_template),
        hcbulletinfig.update_yaxes(title = 'Percentage of total', ticksuffix = '%')    

    else:
        for fueltype in bar_hcbulletinlist:
            hcbulletinfig.add_trace(go.Scatter(x=hc_data['Period'], y=hc_data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype, fill='tonexty', mode = 'none', stackgroup = 'one'         
                                              )),
        hcbulletinfig.add_trace(go.Scatter(x=hc_data['Period'], y=hc_data['Road Fuel gases'].replace(',', '', regex=True).astype(float), 
                                   name='Road Fuel gases', fill='tonexty', mode = 'none', stackgroup = 'one')),        
        for item in line_hcbulletinlist:
            hcbulletinfig.add_trace(go.Line(x=hc_data['Period'], y=hc_data[item].replace(',', '', regex=True).astype(float), 
                                   name=item)),
        hcbulletinfig.update_layout(template=zemo_template)
            
    if hc_selected_chart == 'Quantities':
        hcbulletinfig.update_layout(template=zemo_template),
        hcbulletinfig.update_yaxes(title ='Total hydrocarbon oil quantities (million litres)')
    else:
        hcbulletinfig.update_layout(template=zemo_template)
        hcbulletinfig.update_yaxes(rangemode = 'tozero', title = 'Total receipts value (£ millions)')


    hcbulletinfig.update_xaxes(rangeselector = dict(
                buttons=list([
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=2, label="2Y", step="year", stepmode="backward"),
                                dict(count=4, label="4Y", step="year", stepmode="backward"),
                                dict(count=10, label="10Y", step="year", stepmode="backward"),                    
                                dict(step="all")])
    ))

    
    hcbulletinfig.update_layout(bargap = 0, title = 'HMRC Hydrocarbon Oils Quantities and Receipts (Source: <a href="https://www.gov.uk/government/statistics/hydrocarbon-oils-bulletin">HMRC, Q2 2022</a>)')        

    return hcbulletinfig
       


# ### Interactive CO2 vehicle data visualisation

# In[55]:


@app.callback(Output('veh156fig-graph', 'figure'),
              [Input('veh156-vehicle-picker', 'value')])

def update_veh156fig(veh156_selected_chart):
    
    layout = go.Layout()
    veh156fig = go.Figure(layout=layout)   

    veh156fig_data = veh156[veh156['BodyType']== veh156_selected_chart]
     
    if veh156_selected_chart == 'Cars':
        for fueltype in veh156list:
            veh156fig.add_trace(go.Line(x=veh156fig_data['Date'], y=veh156fig_data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype+' (WLTP)')),
        veh156fig.update_layout(title ='Average reported carbon dioxide (CO2) emission figures of Cars registered for the first time by fuel type<br><sup><i>Total figure will include vehicles with other fuel types, notably battery electric and hybrid electric (diesel) vehicles.</i></sup>'),
    else:
        for fueltype in veh156list_LGV:
            veh156fig.add_trace(go.Line(x=veh156fig_data['Date'], y=veh156fig_data[fueltype].replace(',', '', regex=True).astype(float), 
                                   name=fueltype)),
        veh156fig.update_layout(title = 'Average reported carbon dioxide (CO2) emission figures of Light goods vehicles registered for the first time by fuel type<br><sup><i>Total figure will include vehicles with other fuel types, notably battery electric and hybrid electric (diesel) vehicles</i></sup>')
        veh156fig.update_yaxes(rangemode = 'tozero')
    veh156fig.update_layout(template = zemo_template)
    veh156fig.update_yaxes(title = 'Grams per kilometre')
    veh156fig.update_xaxes(rangeselector = dict(
                buttons=list([
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=2, label="1Y", step="year", stepmode="backward"),                 
                                dict(step="all")])
    ))
    
    return veh156fig


# In[56]:


page_4_layout = html.Div([
    navbar,
    html.H1('Vehicle Data', style={'textAlign': 'center'}),
    html.Div(id='page-4-content'),
    html.Div([
        dcc.Markdown('''
        Future work will incorporate additional DfT stats data tables and new plots that convert fuels sold using energy density figures  

        _Last updated: October 18th, 2022_
                     '''),
                ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                   'backgroundColor':'#FFFFFF',
                   'border': 'thin lightgrey dashed', 
                                   'padding': '6px 0px 0px 8px'}),
dbc.Tabs([
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [ 
    dbc.Row([
            dbc.Col([
                dcc.Markdown('''
                    **Vehicle Parc by fuel type and vehicle category [Source: DfT stats, Q2 2022](https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables)**
                             '''),
                    ], width = width_template)
                ]),
        dbc.Row([
            dbc.Col([
            html.Div([
                dcc.Markdown('''
                    Select vehicle type:            
                    '''),
                dcc.Dropdown(
                    id='vehicle-picker',
                    options=[{'label': x, 'value': x} for x in vehicle_types_parc],
                    value='Car', placeholder='Filter by vehicle type (default is Car)', clearable=False),

            ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                               'padding': '6px 0px 0px 8px'})
                    ], width = width_template),
            dbc.Col([
            html.Div([
                dcc.Markdown('''
                    Choose between Parc and Sales (*Quarterly data only for Bus, Motorcycle and Other*):
                    '''), 
                dcc.Dropdown(
                    id='chart-picker',
                    options=[{'label': x, 'value': x} for x in chart_type],
                    value='Parc', placeholder='Filter by chart type (default is Parc)', clearable=False),

                    ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                               'padding': '6px 0px 0px 8px'})
                    ], width = width_template),

                ]),
        dbc.Row([
            dbc.Col(
            html.Div([   
            dcc.RadioItems(id = 'percentage_button', options = [
                {'label': 'Absolute value', 'value': 'AV'},
                {'label': 'Percentage', 'value': 'PX'}
                                ], value = 'Absolute value')
                ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                               'padding': '6px 0px 0px 8px'}), width = width_template
                    )
                ]),
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id="loading-1",
                    children=[dcc.Graph(id='vehicleparc-graph', responsive = True)],
                    type="circle"), width = width_template
                    )
                ]),        
        ]
                )
                    ), label="Vehicle Parc by fuel type and vehicle category"),
    dbc.Tab(dbc.Card(
        dbc.CardBody(
            [
     dbc.Row([
        dbc.Col(
        html.Div([
        dcc.Markdown('''
            **Quantity and receipts figures for motor spirit fuels, diesel oils, other fuels [Source: HMRC stats National Hydrocarbon bulletin, Q2 2022](https://www.gov.uk/government/statistics/hydrocarbon-oils-bulletin)**
                     '''),
        dcc.Markdown('''
            These statistics report trends for tax liabilities and payments (receipts) by hydrocarbon oil traders but are less effective for analysis of fuels and oils once they’re circulating within the UK economy.
            Total hydrocarbon oils quantities do not include 'road fuel gases (natural gas/liquefied petroleum gas)' as these are reported in kilograms rather than litres. The breakdown of receipts statistics for 
            March 1990 are estimates based on historic quantities released for consumption and duty rates, as only the total receipts figure is available.

            _Next publication is on 28 October 2022_
            ''')]),
            )
        ]),
     dbc.Row([
        dbc.Col([    
            html.Div([
               dcc.Dropdown(
                    id='hc-chart-picker',
                    options=[{'label': x, 'value': x} for x in hc_chart_type],
                    value='Quantities', placeholder='Filter by chart type (default is Quantities)', clearable=False),
               dcc.Markdown('''
                    Choose between Quantities and Receipts _(Note: April, May, June 2022 stats are provisional)_:
                    '''),
                dcc.RadioItems(id = 'hc_percentage_button', options = [
                {'label': 'Absolute value', 'value': 'AV'},
                {'label': 'Percentage', 'value': 'PX'}
                                ], value = 'Absolute value')], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                               'padding': '6px 0px 0px 8px'}),
                ], width = width_template),
            ]),
     dbc.Row([
        dbc.Col(
                    dcc.Loading(
                    id="loading-2",
                    children=[dcc.Graph(id='hcbulletin-graph', responsive = True)],
                    type="circle"), width = width_template
                )
            ])   
            ]
                    )   
                    ), label="HMRC Hydrocarbon Oils Quantities and Receipts"),

    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [    
    dcc.Markdown('''
        **Provisional average reported carbon dioxide (CO2) emission figures of vehicles registered for the first time by body type, fuel type and measure [Source: veh156 DfT, Q2 2022](https://www.gov.uk/government/statistical-data-sets/vehicle-licensing-statistics-data-tables)**
                '''),
    dcc.Markdown('''
        Transitioning to testing under WLTP was made mandatory for most cars in September 2018 and for most light goods vehicles in September 2019. However, the Reported figure used e-NEDC values to maintain tax and monitoring systems. The Reported figure moved to WLTP for cars in April 2020 and for light goods vehicles in March 2021.
        Hybrid Electric (Petrol) and Plug-in Hybrid Electric (Petrol) data for Light Goods Vehicles is not available due to low reliability. 
                '''),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='veh156-vehicle-picker',
                    options=[{'label': x, 'value': x} for x in vehicle_type_veh156],
                    value='Cars', placeholder='Filter by vehicle type (default is Cars)', clearable=False),
                dcc.Loading(
                    id="loading-3",
                    children=[dcc.Graph(id='veh156fig-graph', responsive = True)],
                    type="circle")
                    ], width = width_template),
                ])
        ]
                )
                    ), label="Average reported carbon dioxide emission figures of vehicles registered")    
        ]),

])


# ### Interactive local authority sectoral emissions visualisation

# In[57]:


@app.callback(Output('my-graph', 'figure'),
              [Input('sector-picker', 'value'), Input('region-picker', 'value')])

def update_figure(selected_sector, selected_region):

    filtered_LAem = LAem.copy()
    filtered_LAem = LAem[LAem['Region'].isin(selected_region)]
    filtered_LAem_2 = filtered_LAem[filtered_LAem['LA GHG Sub-sector'] == selected_sector]
    fig = px.choropleth(
        filtered_LAem_2,
        geojson=LA_map2,
        color="CO2 emissions within the scope of influence of LAs (kt CO2e)",
        color_continuous_scale=theme_color_scale, 
        locations="Local Authority",
        featureidkey="properties.LAD21NM",
        projection="mercator",
        hover_name = "Local Authority",
        hover_data=['Local Authority', 'CO2 emissions within the scope of influence of LAs (kt CO2e)', 'LA GHG Sub-sector', 'Region'],
        title='GHG emissions within the scope of influence of LAs',
                        )
    fig.update_geos(fitbounds="geojson", visible=False)
    # Define layout specificities
    fig.update_traces(uirevision = "Don't change")
    fig.update_coloraxes(colorbar_title_text="GHG emissions within the scope of influence of LAs (ktCO2e)", colorbar_orientation = 'v', colorbar_title_font_size = 12, colorbar_title_side = "right", colorbar_ticksuffix = "(kt CO2e)", colorbar_showticksuffix = "none")
    fig.update_layout(margin={"r":0,"t":25,"l":0,"b":0}, template = zemo_template_choro)
    return fig


# In[58]:


TUmode_options = ['Cars', 'Light Commerical Vehicles','Heavy Goods Vehicles','National Rail','TfL Tube','TfL Bus','Bus (excl. London)', 'Cycling']


# In[59]:


page_5_layout = html.Div([
        navbar,
        html.H1('Local Authority Data', style={'textAlign': 'center'}),
        html.Div([
        dcc.Markdown('''
        Future work includes full United Kingdom map and DNO region breakdown

        _Last updated: September 30th, 2022_
                     ''')
                ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                   'backgroundColor':'#FFFFFF',
                   'border': 'thin lightgrey dashed', 
                                   'padding': '6px 0px 0px 8px'}),
dbc.Tabs([
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [ 
    dcc.Markdown('''
        **Public charging infrastructure by Local Planning Authority across Great Britain [Source: DfT, July 2022](https://www.gov.uk/government/statistics/electric-vehicle-charging-device-statistics-july-2022)**
        '''),
    dbc.Row(
        [
            dbc.Col([
            html.Div(
            dcc.Markdown('''
**Public chargepoints (including Rapids)**
        '''), style={'display': 'inline-block'}),  
                dcc.Graph(id = 'LAgraph1',
             figure = fig1,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed', 'border-bottom-style':'hidden'}),
            # style={'display': 'inline-block'}
            ]),
            dbc.Col([
            html.Div(
            dcc.Markdown('''
                **Rapid chargepoints**        
        '''), style={'display': 'inline-block'}),  
                dcc.Graph(id = 'LAgraph2',
             figure = fig2,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed', 'border-bottom-style':'hidden'}),
            # style={'display': 'inline-block'}
                            ]),
        ], align="center",
            ),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id = 'LAgraph3',
             figure = fig3,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed', 'border-top-style':'hidden'}),
          #   style={'display': 'inline-block'}
                            ),
            dbc.Col(dcc.Graph(id = 'LAgraph5',
             figure = fig5,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed', 'border-top-style':'hidden'}),
            # style={'display': 'inline-block'}
                   ),
        ], align="center"),
    html.Br(),
    dcc.Markdown('''
    **These figures show the chargepoint numbers growth rate across different timescales**
                 '''),
     dbc.Row(
         [            
            dbc.Col(dcc.Graph(id = 'LAgraph7',
             figure = fig7,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed'}),
             #style={'display': 'inline-block'}
                   ),
            dbc.Col(dcc.Graph(id = 'LAgraph6',
             figure = fig6,
             responsive = True,
             style={'width': '800', 'border-width':'1', 'border':'thin lightgrey dashed'}),
            # style={'display': 'inline-block'}
                            )
        ], align="center",
             ),
    html.Br(),
    dcc.Markdown('''
    **Carbon dioxide equivalent emissions within the scope of influence of LAs (kt CO2e) [Source: BEIS, 2020](https://www.data.gov.uk/dataset/723c243d-2f1a-4d27-8b61-cdb93e5b10ff/uk-local-authority-and-regional-greenhouse-gas-emissions)**
    '''),
    dbc.Row([
        dbc.Col(html.Div([
                html.Div([
                            dcc.Markdown(children=markdown_text)
                        ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                           'padding': '6px 0px 0px 8px'}),
                html.Div([
                            dcc.Markdown(children=markdown_subtext)
                        ],style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                           'padding': '6px 0px 0px 8px'}),
                dcc.Markdown(''' 
                    Sub-sector of GHG emissions:
                             '''),
                dcc.Dropdown(id='sector-picker', options=sector_options,
                                                 value= 'Total'),
                dcc.Markdown('''
                    Regions:
                             '''),
                dcc.Dropdown(id='region-picker', options=region_options, 
                             placeholder='Filter by region',
                                        value= pcvalueLAdata , multi=True)
                        ], style={'marginLeft': 10, 'marginRight': 0, 'marginTop': 10, 'marginBottom': 10, 
                               'padding': '6px 0px 0px 8px'}), width = 4
               ),
        dbc.Col(
                dcc.Graph(id='my-graph', responsive = True, 
                style={'border-width':'0', 'border':'thin lightgrey dashed'})
                ),
            ]),
        ])
            ), label="Internal geo-spatial Data Visualisation"),
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [
    dbc.Row([
        dbc.Col(
            html.Div([
            dcc.Markdown(''' 
    The [National Map of EV Charge Point Coverage provided by Field Dynamics and supported by ZapMap and Ordinance survey](https://www.field-dynamics.co.uk/research/public-charger-catchment-research/)
    assesses public chargepoint access for households without access to off-street charging space suitable for a small EV ('On-Street households)'. 
    Adequate coverage is defined as being **within 5 minutes walking distance to a public charger**. In their assessment of council areas across Great Britain that are 
    outside of London, it was found that **90%** of these On-Street households are outside of a 5-minute walk to a public charger. '''),            

            html.Iframe(src="https://onstreetcharging.acceleratedinsightplatform.com/",
            style={"height": "800px", "width": "100%", "max-width": "none"}),
                    ]), width='auto'
                )
            ])            
        ]
                )
                    ), label = 'External Local Authority Data Visualisation')
    ])
    

])
    


# In[60]:


ESCsales_chart_types = ['Total sales', 'New sales', 'Parc 2030 and 2035']

ESCsales_vehicle_types = ['Car', 'Van']

ESCsales_list = ESCsales.columns[1:-1]
ESCnewsales_list = ESCnewsales.columns[1:-1]
ESCnewsales_list


# In[61]:


##Unused plotly chart studio charts for modelling graphs

# dcc.Markdown('''
# 2.5 million BEV cars will need to be sold per year in the UK by 2030; a rate 13 times greater than the
# record-breaking levels seen in 2021, consuming as much as 7% of forecast global BEV car
# production.
# '''),
# html.Div([
# html.Iframe(src="https://plotly.com/~Mezo/192/?showlink=false ",
#             style={"height": "800px", "width": "100%", "max-width": "none"}),
#         ], style = style_template),
# html.Br(),
# html.Div([
# html.Iframe(src="https://plotly.com/~Mezo/198/",
#             style={"height": "800px", "width": "100%", "max-width": "none"}),
#         ], style = style_template),
# html.Br(),
# html.Div([
# html.Iframe(src="https://plotly.com/~Mezo/184/",
#             style={"height": "800px", "width": "100%", "max-width": "none"}), 
#         ], style = style_template),


# In[62]:


# Converting chargepoint data to datetime format for buttons

#rslt_df5['Date'] = pd.to_datetime(rslt_df5['Date'])
rslt_df5['Date']
date_format_3 = '%y-%b'
rslt_df5['Date'] = pd.to_datetime(rslt_df5['Date'], format = date_format_3)


# ### Interactive EVET chargepoint modelling visualisation

# In[63]:


@app.callback(Output('ESC-pub', 'figure'), 
              [Input('projection_checklist', 'value')])


def updateESCpub(projection_checklist):
    layout = go.Layout()

    figESCpub = go.Figure(layout=layout)

    if projection_checklist == 'central_case':
        for x in ESCpubheader[1:5]:
            figESCpub.add_trace(go.Scatter(x=ESCpub['Year'].iloc[2:], y=ESCpub[x], name=x, fill='tonexty', mode= 'none', stackgroup = 'one'))
        figESCpub.add_trace(go.Scatter(x=ESCpub['Year'].iloc[2:], y=ESCpub['Total Public Chargepoints'], name='<b>Taskforce Projection (Central case)</b>', mode= 'lines', line = dict(dash='dash', color = '#000000')))
        figESCpub.add_trace(go.Line(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Total'].dropna().astype(int), name="Total Chargepoint Devices"))
    
    elif projection_checklist == 'home':
        figESCpub.add_trace(go.Scatter(x=rslt_df5['Date'], y=EVHSdevices.head(-1).cumsum(), name="EVHS Charging Devices Installed", mode= 'lines'))
        figESCpub.add_trace(go.Scatter(x=ESCpub['Year'].iloc[3:], y=ESCpri['Home Chargepoints'], name='<b>Taskforce Projection</b>', mode= 'lines', line = dict(dash='dash', color='#000000')))
        figESCpub.update_xaxes(rangeselector = dict(
                buttons=list([
                                dict(count=15, label="2020-", step="year", stepmode="backward"),
                                dict(step="all")])
                                )),
    elif projection_checklist == 'all_public':
        figESCpub.add_trace(go.Scatter(x=ESCpub['Year'].iloc[2:], y=ESCpub['Total Public Chargepoints'], name='<b>Taskforce Projection (Central case)</b><sup>1</sup>', mode= 'lines', line = dict(dash='dash', color = '#000000')))
        figESCpub.add_trace(go.Scatter(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Forecast'], name='<br><i>Linear projection based <br>on YoY installations TD</b>', mode= 'lines', line = dict(dash='dash')))
        figESCpub.add_trace(go.Line(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Total'].dropna().astype(int), name="Total Chargepoint Devices"))
    
    else:
        figESCpub.add_trace(go.Scatter(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Forecast'], name='<br><i>Linear projection based <br>on YoY installations 2016-</b>', mode= 'lines', line = dict(dash='dash')))
        figESCpub.add_trace(go.Line(x=ZapMapPUBx['Year'], y=ZapMapPUBx['Total'].dropna().astype(int), name="Total Chargepoint Devices"))
    
    figESCpub.update_yaxes(rangemode="tozero", title = "Number of Chargepoints")
    figESCpub.add_annotation(text='Zemo analysis based on <a href="https://evenergytaskforce.com/reports/ev-energy-taskforce-drivers-for-success-2035/">EVET modelling</a>, <a href="https://www.zap-map.com/statistics/#points">ZapMap</a> and <a href="https://www.gov.uk/government/statistics/electric-vehicle-charging-device-grant-scheme-statistics-january-2022/electric-vehicle-charging-device-grant-scheme-statistics-january-2022#annex-a-evhs-and-wcs-regional-table">DfT</a> reporting data',
                  xref="paper", yref="paper",
                  x=1, y=-0.25, showarrow=False),
    
    figESCpub.update_layout(template=zemo_template, 
    title = '<sup>Central case: Scenario 2 (Mix of uptake for OSR and LRH) with Near Home charging user preferences updated based on ESC extended consumer engagement</sup>'
#            xaxis=dict(
#    autorange=True,
#    range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"],
#    rangeslider=dict(
#        autorange=True,
#        range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"]
    #), type="date"
                )

    return figESCpub


# In[64]:


ESCparc['SMMT'].sum()


# ### Interactive EVET vehicles parc and sales modelling visualisation

# In[65]:


@app.callback(Output('ESCsales-fig', 'figure'), 
              [Input('ESCsales-mode-picker', 'value'), Input('ESCsales-type-picker','value')])


def updateESCvehsales(ESCvehtype, sales_or_newsales):
    layout = go.Layout()

    figESCveh = go.Figure(layout=layout)

    figESCsales_data = ESCsales[ESCsales['Type'].isin(ESCvehtype.split())]
    figESCnewsales_data = ESCnewsales[ESCnewsales['Type'].isin(ESCvehtype.split())]

    if sales_or_newsales == 'Total sales':
        for fueltype in ESCsales_list:
            figESCveh.add_trace(go.Bar(x=figESCsales_data['Year'], y=figESCsales_data[fueltype], name=fueltype))
            figESCveh.update_yaxes(rangemode="tozero", title = 'Percentage of Total sales', ticksuffix = '%')
            figESCveh.update_layout(barmode = 'stack', template = zemo_template, title = 'EVET modelling, Total Vehicle sales')
    
    elif sales_or_newsales == 'Parc 2030 and 2035':
        figESCveh = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])
        figESCveh.add_trace(go.Pie(labels=ESCparc.index, values=ESCparc['2030.0'], name="2030", scalegroup='one', title = '<b>Taskforce modelling, 2030</b><br>Total: ~36,500,000'),
                      1, 1)
        figESCveh.add_trace(go.Pie(labels=ESCparc.index, values=ESCparc['2035.0'], name="2035", scalegroup='one', title = '<b>Taskforce modelling, 2035</b><br>Total: ~36,200,000'),
                      1, 2)
        figESCveh.add_trace(go.Pie(labels=ESCparc.index, values=ESCparc['SMMT'], name="2035", scalegroup='one', title = "<b>SMMT modelling, 2035<br><sup>('Other' from SMMT is assumed to be ICEVs)</sup></b><br>Total: ~35,000,000"),
                      1, 3)
        # Use `hole` to create a donut-like pie chart
        figESCveh.update_traces(hole=0, hoverinfo="label+value+name",
                                marker=dict(line=dict(color='#000000', width=1)))
        figESCveh.update_layout(template = zemo_template,
            title_text="Vehicle parc by powertrain, Taskforce modelling 2030 (LHS) vs. 2035 (Center) vs. SMMT modelling (RHS) ",
            # Add annotations in the center of the donut pies.
            #annotations=[dict(text='2030', x=0.2, y=0.5, font_size=20, showarrow=False),
            #             dict(text='2035', x=0.8, y=0.5, font_size=20, showarrow=False)]
                               )        
    else:
        for fueltype in ESCnewsales_list:
            figESCveh.add_trace(go.Bar(x=figESCnewsales_data['Year'], y=figESCnewsales_data[fueltype], name=fueltype))
            figESCveh.update_yaxes(rangemode="tozero", title = 'Total New sales (millions)')
            figESCveh.update_layout(barmode = 'stack', template = zemo_template, title = 'EVET modelling, Total New sales (millions)')        

    
    
    return figESCveh


# In[66]:


page_6_layout = html.Div([
    navbar,
    html.H1('EVET Modelling Data', style={'textAlign': 'center'}),
    html.Div(id='page-6-content'),
dbc.Tabs([
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [
    html.Div([
    dcc.Markdown('''
            In developing its [analysis](https://evenergytaskforce.com/reports/ev-energy-taskforce-drivers-for-success-2035/), the EV Energy Taskforce employed the Energy Systems Catapult’s latest transport focused
            framework to model the interplay between zero emission vehicles, users and the energy system that
            serves them. The analysis drew upon the collective know-how of the Taskforce’s wide range of stakeholders to
            agree underlying assumptions and scrutinise the outputs.
            
            The work describes outcomes consistent with the goals of the Sixth Carbon Budget. It is predicated on the
            assumption that private sector investment is fundamental, that the preferences of consumers (both private
            and commercial) are reflected, that provision is adequate to meet their needs and that whole system costs are
            minimised. The analysis explored a range of cases and reflects possible conditions in a mature and balanced
            market and provides some clear messages which should inform the development of government policy and
            decisions about industry investment.
    '''),
    dcc.Markdown('''
            In the central case **500,000** public chargepoints need to be deployed by 2035 – from fewer than
            **35,000** in place today – to provide drivers with the confidence to buy electric vehicles and the means to
            charge them.
    '''),
    dcc.Dropdown(id = 'projection_checklist', options = [
        {'label': 'EV Energy Taskforce central case, Public chargepoints', 'value': 'central_case'},
        {'label': 'EV Energy Taskforce central case, Home chargepoints', 'value':'home'},
        {'label': 'Linear projection based on Y-o-Y installations 2016-TD', 'value':'linear'},
        {'label': 'All public chargepoints', 'value':'all_public'},
                        ], value = 'central_case'),
    dcc.Graph(id = 'ESC-pub',
            responsive = True
            ),
        ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                       'padding': '6px 0px 0px 8px'}),
            ])), label = 'Chargepoint Visualisations'),
dbc.Tab(dbc.Card(
    dbc.CardBody(
        [    
    html.Div([
    dcc.Markdown('''
            To meet the UK’s decarbonisation targets, annual BEV sales will need to reach 2.5 million by 2030. To put
            this in context, Deloitte forecasts that global electric car production capacity will be 35 million units in 2030, 
            so sales of electric cars in the UK would represent over 7% of global production capacity in that year.
            By 2035, this could mean 26.8 million BEVs on the road, compared with 337,718 battery electric cars and
            vans today.
            
            From 2030 through 2035, the scale of the electrification of the vehicle parc will put pressure on the
            automotive industry to deliver 18.5 million BEVs to enable their uptake.
    '''),
    dcc.Dropdown(id='ESCsales-type-picker', 
             options=[{'label': x, 'value': x} for x in ESCsales_chart_types],
             placeholder = 'Select chart type',
                                value= 'Total sales'),
    dcc.Dropdown(id='ESCsales-mode-picker', 
             options=[{'label': x, 'value': x} for x in ESCsales_vehicle_types],
             placeholder = 'Select Cars/Vans',
                                value= 'Car'),
    dcc.Graph(id = 'ESCsales-fig',
                responsive = True
                ),

            ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
                                       'padding': '6px 0px 0px 8px'})
            ])), label = 'Vehicle Visualisations')

    
], 
#style={'width': '100%', 'display': 'inline-block'}
)
])


# ### Interactive WPD LCT connections visualisation

# In[67]:


#an API may be possible here

@app.callback(Output('WPDcapacityfig-graph', 'figure'),
              [Input('connection-picker', 'value'), Input('WPDindicator-picker', 'value')])


def update_cxtype(selected_connection, WPDindicator_selected):

    layout = go.Layout()

    xy=WPDcapacity.filter(regex=WPDindicator_selected)
        
    WPDindicator_list = xy.columns.values.tolist()

    WPDcapacityfig = go.Figure(layout=layout)

    if selected_connection == 'Budget Estimates Provided':
        for cxtype in WPDindicator_list:
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2021_BEP['Proposed Connection Voltage (kV)'], y=WPDcapacity2021_BEP[cxtype].cumsum(), name=cxtype + ' 2021', marker_opacity = 0.95))
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2022_BEP['Proposed Connection Voltage (kV)'], y=WPDcapacity2022_BEP[cxtype].cumsum(), name=cxtype + ' May 2022', marker_color = '#007526', marker_opacity = 0.95))                 

    elif selected_connection == 'Connection Offer Not Accepted':
        for cxtype in WPDindicator_list:
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2021_CNA['Proposed Connection Voltage (kV)'], y=WPDcapacity2021_CNA[cxtype].cumsum(), name=cxtype + ' 2021', marker_opacity = 0.95))
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2022_CNA['Proposed Connection Voltage (kV)'], y=WPDcapacity2022_CNA[cxtype].cumsum(), name=cxtype + ' May 2022', marker_color = '#007526', marker_opacity = 0.95))                 

    else:
        for cxtype in WPDindicator_list:
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2021_COA['Proposed Connection Voltage (kV)'], y=WPDcapacity2021_COA[cxtype].cumsum(), name=cxtype + ' 2021', marker_opacity = 0.95))
            WPDcapacityfig.add_trace(go.Bar(x=WPDcapacity2022_COA['Proposed Connection Voltage (kV)'], y=WPDcapacity2022_COA[cxtype].cumsum(), name=cxtype + ' May 2022', marker_color = '#007526', marker_opacity = 0.95))                 


    WPDcapacityfig.update_yaxes(rangemode="tozero", title = "Number of LCT connections and enquiries")
    WPDcapacityfig.update_xaxes(type='category', title = "Grid Connection Voltage (kV)")

    WPDcapacityfig.update_layout(template=zemo_template, title = 'Number of connections per low carbon technology (LCT) on WPD networks<br>from April 2017 to October 2022 (Source: <a href="https://connecteddata.westernpower.co.uk/dataset/lct-enquiries">NGED Connected Data Portal, October 2022</a>)')

    return WPDcapacityfig
#py.plot(wpdLCTconnections, filename = 'wpdLCTconnections', auto_open = False)#


# In[68]:


page_7_layout = html.Div([
    navbar,
    html.H1('Grid Infrastructure Data', style={'textAlign': 'center'}),
    html.Div(id='page-7-content'),
dbc.Tabs([
    dbc.Tab(dbc.Card(
    dbc.CardBody(
        [ 
    html.Div([
    dbc.Row(dbc.Col(
    dcc.Graph(id = 'wpdLCTconnections',
            figure = wpdLCTconnections,
            responsive = True,
            style= style_template
            ), width = width_template)),
    dbc.Row(dbc.Col(
    dcc.Graph(id = 'industryflex',
            figure = industryflex,
            responsive = True,
            style= style_template
            ), width = width_template)),
    dbc.Row(dbc.Col(
    dcc.Graph(id = 'smplot',
            figure = smplot,
            responsive = True,
            style= style_template
            ), width = width_template)),
    dbc.Row(dbc.Col(
    html.Iframe(src="https://plotly.com/~Mezo/85/?showlink=false ",
                style={"height": "800px", "width": "100%"}), width = width_template)),
            ], style = style_template),
        ]
                )
                    ), label = 'External Local Authority Data Visualisation'),
    dbc.Tab(dbc.Card(
        dbc.CardBody(
            [
    html.Div([
    dcc.Dropdown(
        id='connection-picker',
        options=[{'label': x, 'value': x} for x in selected_connection_list],
        value='Budget Estimates Provided',
        placeholder='Filter by connection status (default is Budget Estimates Provided)', multi=True, clearable=False),
    
    dcc.Dropdown(
        id='WPDindicator-picker',
        options=[{'label': x, 'value': x} for x in WPDindicator_list],
        value='Total Demand Capacity (MW)', placeholder='Filter by indicator (default is Total Demand Capacity (MW))', clearable=False),
       
    dcc.Graph(id = 'WPDcapacityfig-graph',
            responsive = True, style = style_template
            )
    ], style = style_template),
            ]
                )
                    ), label = 'Internal National Grid ED (formerly WPD) grid connections monitoring', disabled=True)        
])
    ], style= {'background_color':'#001a70'})


# ### Linking page definitions overall

# In[69]:


# Update the index
@callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-4':
        return page_4_layout
    elif pathname == '/page-5':
        return page_5_layout
    elif pathname == '/page-6':
        return page_6_layout
    elif pathname == '/page-7':
        return page_7_layout    
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


# In[70]:


# Any queries or troubleshooting issues feel free to reach out to me at 
# https://www.linkedin.com/in/mez-edward-benmaamar-a34803172/
# :)


# # 6. Run Server

# In[71]:


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=3007)


# 
