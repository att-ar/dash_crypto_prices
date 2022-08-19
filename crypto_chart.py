import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import numpy as np
import pandas as pd
import plotly.io as pio #templates

#--------------------------------------
#helper function for plotting
def helper(value, j):
    '''
    helper function for data_plot()
    '''
    if value == "None":
        return None
    elif type(value) == list and j < len(value):
        return value[j]
    else:  # not a list so only one value
        if j == 0:
            return value
        else:
            return None


def data_plot(data=None, x=None, y=None,x_title=None, y_title=None, title=None,**kwargs):
    '''
    list of pandas.DataFrame, list of str, list of str, list of str, kwargs -> plotly plot object

    Precondition: If an argument has multiple objects, they must be in a list (can have nested lists).
                  The order of the arguments must be in the same order as the DataFrames.
                  There must be the same number of x columns as y columns passed.

                  ex) ocv_plot(
                      data = [df1, df2],
                      x = [ "SOC", "SOC-Dis" ],
                      y = [ "OCV", "OCV-Dis" ],
                      mode = ["lines+markers", "markers"],
                      color = ["mintcream", "darkorchid"]
                      )

    This function takes one or more DataFrames, columns from the respective DataFrames to be plot on x and y-axes.
    It also takes the mode of plotting desired for the DataFrames and optional keyword arguments.
    It outputs a plotly plot of the data from the columns that were passed.

    Parameters:
    `data` DataFrame or list of DataFrames

    `x` list of columns or nested lists of columns
        example of each option in order:
            x = ["SOC-Dis"]
            x = ["SOC-Dis","SOC-Chg","SOC"]
            x = [ ["Test Time (sec)","Step Time (sec)"], "Step"]
                Test Time and Step Time are both from the same DataFrame; there must be two y columns as well.

    `y` list of columns or nested lists of columns
        View `x` for help

    `x_title` str
        the name of the x_axis to be displayed
        else None

    `y_title` str
        the name of the y_axis to be displayed
        else None

    `title` str
        The title of the Plot
        default None will not add a title

    **kwargs:

    `size` int/float, list of int/float or nested lists of int/float
        same principle as above arguments
        assigns the size of the individual data lines
        if no value is passed, plotly will do it automatically.
    '''
    if type(data) == list and not pd.Series(
        pd.Series([len(x), len(y)]) == len(data)
    ).all():
        return '''Error: x and y columns passed much match the number of DataFrames passed
        Use nested lists for multiple columns from the same DataFrame
        '''

    elif type(data) != list and not pd.Series(pd.Series([len(x), len(y)]) == 1).all():
        return '''Error: x and y columns passed much match the number of DataFrames passed
        Use nested lists for multiple columns from the same DataFrame
        '''

    if "size" in kwargs.keys():
        if type(kwargs["size"]) == list and len(kwargs["size"]) > len(data):
            return "Error: passed more sizes than DataFrames"

    frame = pd.DataFrame(data={"x": x, "y": y})

    for i in ["size"]:
        frame = frame.join(
            pd.Series(kwargs.get(i), name=i, dtype="object"),
            how="outer")

    frame.fillna("None", inplace=True)

    figure = make_subplots(
        x_title = x_title,
        y_title = y_title,
        subplot_titles = [title])

    color_dict = {
        "Solana-SOL":"purple",
        "Litecoin-LTC":"lightblue",
        "Etherium-ETH":"pink",
        "Dogecoin-DOGE":"orange",
        "Bitcoin-BTC":"orchid",
        "Binancecoin-BNB":"yellow",
        "Cardano-ADA":"azure"
        }

    for i in frame.index:
        if type(data) == list:
            use_data = data[i]
        else:
            use_data = data

        if type(frame["x"][i]) == list:  # y[i] must be a list
            for j in range(len(x[i])):
                use_x = frame.loc[i, "x"][j]
                use_y = frame.loc[i, "y"][j]
                use_size = helper(frame.loc[i, "size"], j)

                figure.add_trace(
                    go.Scatter(
                        x=use_data[use_x],
                        y=use_data[use_y],
                        marker={"size": use_size, "color": color_dict[use_y]},
                        name=use_y)
                )
        else:  # x[i] and y[i] are not lists
            use_x = frame.loc[i, "x"]
            use_y = frame.loc[i, "y"]
            use_size = helper(frame.loc[i, "size"], 0)
            # zero is just a placholder

            figure.add_trace(
                go.Scatter(
                    x=use_data[use_x],
                    y=use_data[use_y],
                    marker={"size": use_size, "color": color_dict[use_y]},
                    name=use_y)
            )
    figure.update_yaxes(type = "log")
    return figure

#-------------------------------------------------

df = pd.read_csv("crypto_value.csv")
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df.columns = ["date",
              "Solana-SOL",
              "Litecoin-LTC",
              "Etherium-ETH",
              "Dogecoin-DOGE",
              "Bitcoin-BTC",
              "Binancecoin-BNB",
              "Cardano-ADA"]
df.replace({0:np.nan}, inplace=True)

fig = data_plot(
    data = df,
    x = [["date"]*3],
    y = [["Bitcoin-BTC","Etherium-ETH","Litecoin-LTC"]],
    title = "Cryptocurrency Prices 2018-2022",
    x_title = "Date",
    y_title = "Price (USD)"
)

app = dash.Dash(__name__)
app.title = "Cryptocurrency Prices 2018-2022"
server = app.server


app.layout = html.Div(
    id = "app-container",
    children = [
        html.Div(id = "header-area",
        style = {"backgroundColor": "black"},
        children = [
            html.H1(id = "header-title",
                    style = {"color":"white", "fontFamily":"Verdana, sans-sherif"},
                    children = "Cryptocurrency Prices from 2018-2022"),
            html.P(id = "header-description",
                   style = {"color":"white", "fontFamily":"Verdana, sans-sherif"},
                   children = "Cost of various crypto coins from 2018-22")
                    ]
                ),
        html.Div(
            id="menu-area",
            children=[
                html.Div(
                    children = [
                        html.Div(
                        className="menu-title",
                        children="Cryptocurrencies"
                        ),
                        dcc.Dropdown(
                        id="crypto-filter",
                        className="dropdown",
                        options=[{"label": coin, "value":coin} for coin in df.columns[1:]],
                        clearable=False,
                        value = ["Bitcoin-BTC","Etherium-ETH","Litecoin-LTC"],
                        multi = True
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title",
                            children="Date Range"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df.date.min().date(),
                            max_date_allowed=df.date.max().date(),
                            start_date=df.date.min().date(),
                            end_date=df.date.max().date()
                        )
                    ]
                )
            ]
        ),

        html.Div(id = "graph-container",
        children = dcc.Graph(id = "price-chart",
                             figure = fig,
                             config={"displayModeBar":False})
                )
            ]
        )


@app.callback(
Output("price-chart", "figure"),
Input("crypto-filter", "value"),
Input("date-range","start_date"),
Input("date-range","end_date")
)
def update_chart(cryptos, start_date, end_date):
    #plotly fig
    filtered_data = df.loc[(df.date >= start_date) & (df.date <= end_date)]
    fig = data_plot(
        data = filtered_data,
        x = [["date"]*len(cryptos)],
        y = [cryptos],
        title = "Cryptocurrency Prices 2018-2022",
    )

    fig.update_layout(
        template="plotly_dark",
        legend = {"title":"Cryptocurrencies"},
        xaxis_title = "Date",
        yaxis_title = "Price (USD)",
        font = dict(
            family="Verdana, sans-sherif",
            size=14,
            color="white"
        )
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
