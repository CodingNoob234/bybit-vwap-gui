import bybit
import time
import pandas as pd
from datetime import datetime
import settings

import logging
LOGGER = logging.getLogger(__name__)

class ByBit:
    def __init__(self):
        """
        Initializes parameters and logs in to ByBit exchange
        """
        
        LOGGER.info("Initialising client")
        
        self.client = bybit.bybit(test=False, 
            api_key = settings.API_KEY, 
            api_secret = settings.API_SECRET,
            )
        self.current_interval = 0
        self.calculate_fully = True
        self.calculate_temp = True

    def get_price_hist(self,interval, length = 60, symbol = "BTCUSD"):
        """
        Returns [open, high, low, close, volume] history of ~250(?) ticks for a given interval
        """
        if interval != self.current_interval:
            self.calculate_fully = True
            self.current_interval = interval
        hist = self.client.Kline.Kline_get(symbol=symbol, interval=f"{interval}", **{"from":time.time() - length * 60 * interval}).result()[0]['result']

        self.df = pd.DataFrame(hist)
        self.df = self.df[["open_time", "open", "high", "low", "close", "volume"]]
        self.df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        for c in self.df.columns:
            self.df.loc[:, c] = self.df[c].apply(lambda x: float(x))
        self.df["Date"] = self.df.Date.apply(lambda x: datetime.fromtimestamp(x))
        self.df = self.df.set_index("Date", drop=True)

    def get_vwap_bollinger_bands(self, factor2 = 1.96, factor3 = 3, factor4 = 4, period = 14):
        """
        Determines where to place buy and sell orders using VWAP indicator
        """
        self.df["adj_price"] = 1/3 * (self.df["High"] + self.df["Low"] + self.df["Close"])
        self.df["vwap"] = (self.df.adj_price * self.df.Volume).rolling(period).sum() / self.df.Volume.rolling(period).sum()
        self.df["rolling_std"] = self.df.adj_price.rolling(period).std()

        self.df["0std"] = self.df.vwap
        self.df["2std"] = self.df.vwap + factor2 * self.df.rolling_std
        self.df["-2std"] = self.df.vwap - factor2 * self.df.rolling_std
        self.df["3std"] = self.df.vwap + factor3 * self.df.rolling_std
        self.df["-3std"] = self.df.vwap - factor3 * self.df.rolling_std
        self.df["4std"] = self.df.vwap + factor4 * self.df.rolling_std
        self.df["-4std"] = self.df.vwap - factor4 * self.df.rolling_std
