import dash
from flask import Flask, render_template,send_from_directory
from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import os
# Load the dataset
data = pd.read_csv("predicted_crime.csv")

# Filter and sort data for top 10 high-risk districts
high_risk = data[data["Predicted Change in Crime Pct 2014-2015"] > 0]
top_10 = high_risk.nlargest(10, "Predicted Change in Crime Pct 2014-2015")

# Initialize Flask app
server = Flask(__name__, template_folder=os.path.abspath("../main_website"), static_folder="../main_website")


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
    server=server,  # Link Dash app to Flask
    url_base_pathname="/dash2/",  # Dash app will be accessible at /card_two/
)

# Dash Layout for Card 2
dash_app.layout = html.Div(
    [
        dcc.Graph(
            id="high-risk-districts",
            style={"height": "500px"},
        ),
    ]
)

# Callback to update the bar chart
@dash_app.callback(
    dash.dependencies.Output("high-risk-districts", "figure"),
    dash.dependencies.Input("high-risk-districts", "id"),  # Dummy input to load the chart
)
def update_high_risk_chart(_):
    # Create the bar chart
    fig = px.bar(
        top_10,
        x="DISTRICT",
        y="Predicted Change in Crime Pct 2014-2015",
        title="Top 10 High-Risk Districts for 2015",
        labels={"DISTRICT": "District", "Predicted Change in Crime Pct 2014-2015": "Predicted Change (%)"},
        hover_data=["STATE/UT", "Predicted Change in Crime Pct 2014-2015"],
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return fig

if __name__ == "__main__":
    server.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))