import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# ======================================================
# CONFIG
# ======================================================
DATA_PATH = "ecuador_gldas_enriquecido_solo_tierra.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["time"])

# Variables disponibles
variables = [
    "SoilMoi0_10cm_inst",
    "SoilMoi10_40cm_inst",
    "RootMoist_inst",
    "SoilTMP0_10cm_inst",
    "Tair_f_inst",
    "Rainf_tavg",
    "Evap_tavg",
]

# ======================================================
# APP
# ======================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server  # <-- necesario para Gunicorn

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("AGRO-LEO ECUADOR • GLDAS"), width=12),
        dbc.Col(html.P("Monitoreo climático/suelo para agricultura (2020–2024)"), width=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Variable"),
            dcc.Dropdown(variables, "SoilMoi0_10cm_inst", id="sel-var")
        ], md=4),
        dbc.Col([
            html.Label("Provincia"),
            dcc.Dropdown(df["provincia"].dropna().unique(), None, id="sel-prov", multi=True)
        ], md=4),
        dbc.Col([
            html.Label("Rango de fechas"),
            dcc.DatePickerRange(
                id="sel-dates",
                min_date_allowed=df["time"].min(),
                max_date_allowed=df["time"].max(),
                start_date=df["time"].min(),
                end_date=df["time"].max()
            )
        ], md=4),
    ], className="mb-4"),

    dcc.Tabs(id="tabs", value="mapa", children=[
        dcc.Tab(label="🗺️ Mapa", value="mapa"),
        dcc.Tab(label="📈 Serie temporal", value="serie"),
        dcc.Tab(label="📊 Distribución", value="dist"),
        dcc.Tab(label="🌳 Clasificación", value="clasif"),
    ]),
    html.Div(id="tab-content", className="p-4")
], fluid=True)


# ======================================================
# CALLBACKS
# ======================================================
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("sel-var", "value"),
    Input("sel-prov", "value"),
    Input("sel-dates", "start_date"),
    Input("sel-dates", "end_date")
)
def render_tab(tab, var, provs, d1, d2):
    dff = df.copy()
    dff = dff[(dff["time"] >= d1) & (dff["time"] <= d2)]
    if provs:
        dff = dff[dff["provincia"].isin(provs)]

    if tab == "mapa":
        fig = px.scatter_mapbox(
            dff, lat="lat", lon="lon", color=var, size_max=6,
            mapbox_style="carto-positron", zoom=5, height=500
        )
        return dcc.Graph(figure=fig)

    elif tab == "serie":
        dff_m = dff.groupby("time")[var].mean().reset_index()
        fig = px.line(dff_m, x="time", y=var, markers=True)
        return dcc.Graph(figure=fig)

    elif tab == "dist":
        fig = px.histogram(dff, x=var, nbins=40)
        return dcc.Graph(figure=fig)

    elif tab == "clasif":
        return html.Div([
            html.H5("Aquí iría tu modelo de clasificación 🌳"),
            html.P("Puedes añadir callbacks para entrenar y mostrar árbol.")
        ])

    return html.Div("Selecciona una pestaña")


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
