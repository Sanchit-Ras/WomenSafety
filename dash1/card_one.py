from flask import Flask, render_template, send_from_directory
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# Load the dataset
data = pd.read_csv("crime_data_features_no_lag.csv")

# Preprocess data
year_columns = [col for col in data.columns if "Change in Crime Pct" in col]

# Compute yearly averages, ignoring years with negative averages
yearly_avg = []
for col in year_columns:
    avg = data[col].mean()
    yearly_avg.append({"Year": col.split()[-1], "Average Crime Pct": avg})

yearly_avg_df = pd.DataFrame(yearly_avg)

# Initialize Flask app
server = Flask(__name__, template_folder=os.path.abspath("../main_website"), static_folder=os.path.abspath("../main_website"))  # Keep original configuration

# Serve static files explicitly from the root directory
@server.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)

# Route for the main website
@server.route("/")
def index():
    return render_template("index.html")

# Initialize Dash app
dash_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash1/",
)

# Dash Layout
dash_app.layout = html.Div(
    [
        html.Script("""
        document.addEventListener('DOMContentLoaded', function() {
            const width = window.innerWidth;
            const widthInput = document.getElementById('screen-width');
            widthInput.value = width;
            widthInput.dispatchEvent(new Event('change'));
        });
        """, type="text/javascript"),

        # Hidden input field to store screen width
        dcc.Input(id='screen-width', type='hidden', value=800),

        dcc.Graph(
            id="yearly-trends",
            style={"height": "500px"},
            config={"displayModeBar": False},
        ),
        html.Div(id="district-chart"),
    ]
)

# Callback for updating the yearly chart
@dash_app.callback(
    Output("yearly-trends", "figure"),
    Input("yearly-trends", "clickData"),
)
def update_yearly_chart(screen_width):
    fig = px.line(
        yearly_avg_df,
        x="Year",
        y="Average Crime Pct",
        title="Yearly Crime Percentage Trends (2001-2014)",
        markers=True,
        labels={"Average Crime Pct": "Average Change (%)"},
        hover_data={"Year": True, "Average Crime Pct": True},
    )
    # Responsive layout adjustments
    if screen_width and int(screen_width) < 640:
        fig.update_layout(
            title_font_size=9,
            xaxis_title_font_size=6,
            yaxis_title_font_size=6,
            margin=dict(l=15, r=15, t=25, b=25),
        )
    else:
        fig.update_layout(
            title_font_size=16,
            xaxis_title_font_size=12,
            yaxis_title_font_size=12,
            margin=dict(l=40, r=40, t=50, b=50),
        )

    fig.update_layout(clickmode="event+select")
    return fig


# Callback for generating district-level chart
@dash_app.callback(
    Output("district-chart", "children"),
    Input("yearly-trends", "clickData"),
)
def display_district_chart(click_data):
    if click_data:
        year = click_data["points"][0]["x"]
        year_col = f"Change in Crime Pct {year}"

        # Filter data for positive values only
        filtered_data = data[data[year_col] > 0]

        # Create the district-level chart
        fig = px.bar(
            filtered_data,
            x="DISTRICT",
            y=year_col,
            title=f"District-Level Crime Trends for {year}",
            labels={"DISTRICT": "District", year_col: "Crime Increase (%)"},
            hover_data=["STATE/UT", year_col],
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})

        return dcc.Graph(figure=fig, style={"height": "500px"})
if __name__ == "__main__":
    server.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
