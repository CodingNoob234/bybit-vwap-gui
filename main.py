from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num
from datetime import datetime
from modules.broker import ByBit
import settings
import logging
from configure_logger import configure_logger
configure_logger()
LOGGER = logging.getLogger(__name__)

class Application(Frame):
    def __init__(self, master, period=14):
        super().__init__(master)
        self.master = master
        self.self = self

        try:
            self.period = settings.VWAP_PERIOD
        except AttributeError:
            self.period = period
        self.stop = True

        self.create_widgets()
        self.set_up_broker()
        self.create_canvas()

    def create_widgets(self):
        """Add buttons and menus to the application."""
        # Start/stop/quit buttons
        self.start_button = Button(
            self.master,
            text="START",
            command=self.run
        )
        self.start_button.place(x=0, y=0, relwidth=0.05)

        self.stop_button = Button(
            self.master,
            text="STOP",
            command=self.stop_plotting
        )
        self.stop_button.place(x=60, y=0, relwidth=0.05)

        self.quit = Button(
            self.master,
            text="QUIT",
            fg="red",
            command=self.master.destroy
        )
        self.quit.place(x=120, y=0, relwidth=0.05)

        # Text widget to display the last refresh time
        self.text = Label(self.master, text='')
        self.text.place(x=0, y=29)

        # Create option menu to select frequency
        OPTIONS = ('1', '5', '15', '60', '240')
        self.variable = StringVar(self.master)
        self.variable.set(OPTIONS[1])  # Default value
        self.w = OptionMenu(self.master, self.variable, *OPTIONS)
        self.w.place(x=183, y=4.25, relwidth=0.045)

    def create_canvas(self):
        fig = plt.figure()
        fig.subplots_adjust(left=0.06, bottom=0.05, right=0.98, top=0.98, wspace=None, hspace=None)
        self.ax_candle = fig.add_subplot(111)
        self.ax_candle.xaxis_date()
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        toolbar.update()
        self.canvas.get_tk_widget().place(x=0, y=55, relheight=0.8, relwidth=1)

    def set_up_broker(self):
        self.ex = ByBit()

    def stop_plotting(self):
        LOGGER.info("Stop button pressed")
        self.stop = True

    def run(self):
        LOGGER.info("Start button pressed")
        if self.stop == False:
            LOGGER.info("Was already plotting...")
        else:
            self.stop = False
            self.refresh_plot()

    def refresh_plot(self):
        if not self.stop:
            start = datetime.strftime(datetime.now(), "%H:%M:%S.%f")
            self.ax_candle.clear()
            self.ex.get_price_hist(symbol=settings.SYMBOL, interval=int(self.variable.get()))
            self.ex.get_vwap_bollinger_bands(period=self.period)
            data = self.ex.df
            ohlc = []
            for date, row in self.ex.df.iterrows():
                openp, highp, lowp, closep = row[:4]
                ohlc.append([date2num(date), openp, highp, lowp, closep])
            self.ax_candle.plot(data.index, data["3std"], label="+3STD")
            self.ax_candle.plot(data.index, data["-3std"], label="-3STD")
            self.ax_candle.plot(data.index, data["2std"], label="+2STD")
            self.ax_candle.plot(data.index, data["0std"], label="+0STD")
            self.ax_candle.plot(data.index, data["-2std"], label="-2STD")
            self.ax_candle.plot(data.index, data["4std"], label="+4STD")
            self.ax_candle.plot(data.index, data["-4std"], label="-4STD")
            candlestick_ohlc(self.ax_candle, ohlc, colorup="g", colordown="r",
                             width=int(self.variable.get()) / (1.5 * 24 * 60))
            self.ax_candle.grid()
            self.canvas.draw()

            end = datetime.strftime(datetime.now(), "%H:%M:%S.%f")
            self.text.config(text=f'Last updated at: {end}')

            LOGGER.debug(f'Refreshed plot from {start} to {end}')

            self.after(1, self.refresh_plot)  # After 1 ms, repeat the function

if __name__ == "__main__":
    root = Tk()
    root.geometry("1200x1600")
    app = Application(master=root)
    app.mainloop()
