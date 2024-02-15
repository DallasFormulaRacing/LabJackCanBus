import time
import board
import busio
import adafruit_lsm303_accel
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_lsm303_accel.LSM303_Accel(i2c)

df = pd.DataFrame(columns=["time", "x", "y", "z"])

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Graph(id='graph-content'),
    dcc.Interval(id="update-interval", interval=500)
])

@callback(
    Output('graph-content', 'figure'),
    Input("update-interval", "value")
)
def update_graph(value, _n):
    accel_x, accel_y, accel_z = accelerometer.acceleration
    
    print('Acceleration (m/s^2): x={0:0.3f}, y={1:0.3f}, z={2:0.3f}'.format(accel_x, accel_y, accel_z), end="\r")
    df = df.append({"time": time.time(), "x": accel_x, "y": accel_y, "z": accel_z})
    return px.line(df, x='time', y=["x", "y", "z"])

if __name__ == '__main__':
    app.run(debug=True)

