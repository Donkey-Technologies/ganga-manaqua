import boto3
import os
from os.path import dirname, abspath
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np
from datetime import datetime


def get_table_name():
    ddb_table_path = os.path.join(dirname(abspath(__file__)), "ddb_table.txt")
    try:
        with open(ddb_table_path, "r") as f:
            for line in f:
                if ":" in line:
                    _, table_name = line.strip().split(":", 1)
        return table_name

    except OSError:
        print("Unable get the table name")
        return ""


def get_dynamodb_data():
    # Get the table name
    table_name = get_table_name()

    # Configure DynamoDB Connection
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    respuesta = table.scan()

    return respuesta["Items"]


css_path = os.path.join(dirname(abspath(__file__)), "assets", "styles.css")
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css",
        dbc.themes.LUX,
        css_path,
    ],
    suppress_callback_exceptions=True,
)


def create_navbar():
    navbar = dbc.NavbarSimple(
        brand=html.H1("Ganga Manaqua Project", style={"color": "white"}),
        brand_href="#",
        dark=True,
        className="custom-navbar-color",
    )
    return navbar


def create_psicrometry_plot():
    temperaturas = np.linspace(0, 40, 100)

    fig = go.Figure()

    for r_hum in np.arange(0.1, 1.0, 0.1):
        dp = dew_point(temperaturas, r_hum * 100)
        fig.add_trace(
            go.Scatter(x=temperaturas, y=dp, mode="lines", name=f"RH {r_hum*100:.0f}%")
        )

    fig.update_layout(
        title="Psicrometric Analisys",
        xaxis_title="Temperature (°C)",
        yaxis_title="Dew Point (°C)",
        legend_title="Relative Humidity",
    )

    return dcc.Graph(figure=fig)


def dew_point(T, RH):
    a = 17.27
    b = 237.7
    alpha = ((a * T) / (b + T)) + np.log(RH / 100.0)
    return (b * alpha) / (a - alpha)


def create_series_fig(inlet, outlet, time):
    inlet = go.Scatter(x=time, y=inlet, mode="lines", name="Inlet")
    outlet = go.Scatter(x=time, y=outlet, mode="lines", name="Outlet")

    fig = {
        "data": [inlet, outlet],
        "layout": {
            "title": "Temperature Progression",
            "xaxis_title": "Time",
            "yaxis_title": "Temperature (°C)",
        },
    }

    fig["layout"]["legend"] = {"x": 0, "y": 1.2, "orientation": "h"}

    return fig


def create_inlet_outlet_plots():
    # Get data
    data = get_dynamodb_data()
    data_sorted = sorted(
        data, key=lambda x: datetime.strptime(x["TimeStamp"], "%Y-%m-%d %H:%M:%S")
    )

    # TODO select a certain data range
    data = data[:-60]

    timestamps = [
        datetime.strptime(entry["TimeStamp"], "%Y-%m-%d %H:%M:%S")
        for entry in data_sorted
    ]
    inlet_temperatures = [float(entry["inlet_temp"]) for entry in data_sorted]
    outlet_temperatures = [float(entry["outlet_temp"]) for entry in data_sorted]
    inlet_humidities = [float(entry["inlet_hum"]) for entry in data_sorted]
    outlet_humidities = [float(entry["outlet_hum"]) for entry in data_sorted]

    inlet_outlet_plots = (
        [
            dbc.Col(
                dcc.Graph(
                    figure=create_series_fig(
                        inlet_temperatures, outlet_temperatures, timestamps
                    )
                ),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(
                    figure=create_series_fig(
                        inlet_humidities, outlet_humidities, timestamps
                    )
                ),
                width=6,
            ),
        ],
    )
    return inlet_outlet_plots[0]


def create_app_content():
    app_plots_body = html.Div(
        [
            dbc.Row(
                create_inlet_outlet_plots(),
                style={"marginTop": "25px"},
            ),
            dbc.Row(
                create_psicrometry_plot(),
                style={"marginTop": "25px"},
            ),
        ]
    )

    return app_plots_body


def create_contact_info():
    url_github = "https://github.com/nachoDRT"
    github_link = html.Div(
        [
            html.A(
                [
                    html.Div(
                        [html.I(className="bi bi-github"), " nachoDRT"],
                    )
                ],
                href=url_github,
                target="_blank",
                style={"color": "white", "text-decoration": "none"},
            )
        ]
    )

    contact = dbc.Row(
        [
            dbc.Col(
                github_link,
                className="footer-col",
            )
        ],
        className="footer-container",
    )

    return contact


def create_footer():
    return html.Footer(create_contact_info())


app.layout = html.Div(
    [
        create_navbar(),
        dbc.Row(
            [
                dbc.Col(width=2),
                dbc.Col(create_app_content(), width=8, style={"margin": "0 auto"}),
                dbc.Col(width=2),
            ]
        ),
        create_footer(),
    ]
)

app.run_server(debug=True)
