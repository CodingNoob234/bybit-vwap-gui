# bybit-vwap-gui
As an introduction to TKinter, I build this simple application that shows bitcoin price data from exchange ByBit. The application plots ohlc-candlebars of the past trading history. As indicators, the VWAP alongside the Bollinger bands are plotted as well. The user can determine for which frequency (1/5/15/60/240 minutes) the candlebars are shown.

It is adviced to create a virtual enviroment to install the dependencies in.
To do so, run the following commands:
 - ``` conda create --name temp-env python=3.9.16```
 - ``` conda activate temp-env ```
 - ``` pip install -r requirements.txt ```

To run the application it is crucial to define a settings.py file in the root of the project, where the following properties are defined:
| Property Name | Default | Description |
|-----------|---------|-------------|
| LOG_LEVEL | INFO | Logging level of the application |
| SYMBOL | BTCUSD | A valid product symbol on bybit |
| API_KEY** | None | A valid api key from your bybit account |
| API_SECRET** | None | A valid api secret from your bybit account |
**The API credentials are currently not used. If later on account specific metrics are added, this could be implemented. Currently these can be set to any string value or None.