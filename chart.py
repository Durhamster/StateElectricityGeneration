import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

# Data
df = pd.read_excel("data/electricity_generation.xlsx", sheet_name="2019").sort_values(
    by=["STATE"], axis=0, ascending=True
)

# For the drop down menu
state_options = df["STATE (FULL NAME)"].unique()

# bootstrap theme
external_stylesheets = [dbc.themes.LITERA]

# The Layout of the App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Electricity Generation By State"

app.layout = html.Div(
    [
        # Main Container
        dbc.Container(
            [
                dbc.Row(
                    html.H2("Electricity Generated by Source (in Megawatthours)", className="mt-2",),
                ),
                dbc.Row(
                    html.Div(
                        [
                            dcc.Dropdown(
                                className="dropdown",
                                id="STATE",
                                options=[
                                    {"label": i, "value": i} for i in state_options
                                ],
                                value="All States",
                                clearable=False,
                            ),
                        ],
                        style={"width": "25%", "display": "inline-block"},
                    ),
                ),
                dbc.Spinner(
                    html.Div(
                    [
                    dbc.Row(
                        dcc.Graph(className="piegraph", id="pie-graph", config={"displayModeBar": False}),
                    ),
                    ],
                    className="d-flex justify-content-center",
                ),
                color="primary",
                )
            ]
        )
    ],
    className="loading"
)

# Call back functions
@app.callback(
    dash.dependencies.Output("pie-graph", "figure"),
    [dash.dependencies.Input("STATE", "value")],
)
def update_graph(State):
    if State == "All States":
        df_plot = df.copy()
    else:
        df_plot = df[df["STATE (FULL NAME)"] == State]

    # Clean data so slices under 1% do not appear
    pv = pd.pivot_table(
        df_plot,
        index=["ENERGY SOURCE"],
        values=["GENERATION (Megawatthours)"],
        aggfunc=sum,
        fill_value=0,
    ).reset_index()

    # Combines all sources under 1% into 'Other'
    # Find total megawatthours and what 1% is for selected state
    total_megawatthours = pv["GENERATION (Megawatthours)"].sum(axis=0, skipna=True)
    one_percent = total_megawatthours * 0.01
    pv.loc[pv["GENERATION (Megawatthours)"] <= one_percent, "ENERGY SOURCE"] = "Other"
    pv.sort_values(by=["ENERGY SOURCE"], inplace=True)

    # Colors for chart
    colors_ls = [
        "gold",
        "mediumturquoise",
        "darkorange",
        "lightgreen",
        "blue",
        "lightpurple",
        "ruby",
    ]

    # Pie Chart
    pie_chart = dict(
        data=[
            go.Pie(
                labels=pv["ENERGY SOURCE"],
                values=pv["GENERATION (Megawatthours)"],
                textfont_size=18,
                marker=dict(
                    colors=colors_ls,
                ),
                sort=False,
            )
        ],
        layout=dict(
            title=f"<b style='font-size:26'>{State}</b>",
            autosize=True,
            font=dict(family="Arial", size=12, color="white"),
            margin=dict(l=0, r=0, b=40, t=85, pad=0),
            dragmode=False,
            paper_bgcolor="#2c3a47"
        ),
    )

    return pie_chart


if __name__ == "__main__":
    app.run_server(debug=True)