# from multiprocessing import Process
# import os

# # Import your Flask apps
# from card_one import server as app1
# from card_two import server as app2

# def run_app1():
#     """Run the first Flask app on port 5000."""
#     os.environ["FLASK_APP"] = "card_one.py"
#     os.environ["FLASK_ENV"] = "development"
#     app1.run(port=5000)

# def run_app2():
#     """Run the second Flask app on port 5001."""
#     os.environ["FLASK_APP"] = "card_two.py"
#     os.environ["FLASK_ENV"] = "development"
#     app2.run(port=5001)

# if __name__ == "__main__":
#     # Create separate processes for each Flask app
#     p1 = Process(target=run_app1)
#     p2 = Process(target=run_app2)

#     # Start the processes
#     p1.start()
#     p2.start()

#     # Wait for the processes to finish (they won't unless you stop them manually)
#     p1.join()
#     p2.join()
from flask import Flask, render_template,send_from_directory
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
import dash
# # Import card_one and card_two
# from card_one import dash_app as dash_app1
# from card_two import dash_app as dash_app2
data = pd.read_csv("crime_data_features_no_lag.csv")

# Preprocess data
year_columns = [col for col in data.columns if "Change in Crime Pct" in col]

# Compute yearly averages, ignoring years with negative averages
yearly_avg = []
for col in year_columns:
    avg = data[col].mean()
    yearly_avg.append({"Year": col.split()[-1], "Average Crime Pct": avg})

yearly_avg_df = pd.DataFrame(yearly_avg)


data = pd.read_csv("predicted_crime.csv")

# Filter and sort data for top 10 high-risk districts
high_risk = data[data["Predicted Change in Crime Pct 2014-2015"] > 0]
top_10 = high_risk.nlargest(10, "Predicted Change in Crime Pct 2014-2015")

# Create a single Flask server
server = Flask(__name__, template_folder=".",static_folder=".")

# @server.route('/<path:filename>')
# def serve_static(filename):
#     return send_from_directory(os.getcwd(), filename)

# Register the main index route
@server.route("/")
def index():
    return render_template("index.html")

# Integrate Dash apps with different routes
dash_app1 = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash1/",
)
dash_app2 = Dash(
    __name__,
    server=server,
    url_base_pathname="/dash2/",
)

# Dash app 1 Layout
dash_app1.layout = html.Div(
    [
        dcc.Graph(
            id="yearly-trends",
            style={"height": "500px"},
            config={"displayModeBar": False},
        ),
        html.Div(id="district-chart"),
    ]
)

# Callback for updating the yearly chart
@dash_app1.callback(
    Output("yearly-trends", "figure"),
    Input("yearly-trends", "clickData"),
)
def update_yearly_chart(_):
    fig = px.line(
        yearly_avg_df,
        x="Year",
        y="Average Crime Pct",
        title="Yearly Crime Percentage Trends (2001-2014)",
        markers=True,
        labels={"Average Crime Pct": "Average Change (%)"},
        hover_data={"Year": True, "Average Crime Pct": True},
    )
    fig.update_layout(clickmode="event+select")
    return fig


# Callback for generating district-level chart
@dash_app1.callback(
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


# Dash app 2 layout
dash_app2.layout = html.Div(
    [
        dcc.Graph(
            id="high-risk-districts",
            style={"height": "500px"},
        ),
    ]
)

# Callback to update the bar chart
@dash_app2.callback(
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
    server.run(debug=True)