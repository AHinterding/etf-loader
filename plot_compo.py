import datetime as dt

from etf_mapper import CompoMapper

if __name__ == '__main__':
    mapper = CompoMapper()

    plot_date = dt.date.today()  # Download data first before running!
    mapper.plot(plot_date, 'WOOD')
