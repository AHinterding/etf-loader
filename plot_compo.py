from etf_mapper.compo_mapper import CompoMapper
import datetime as dt

if __name__ == '__main__':
    mapper = CompoMapper()

    plot_date = dt.date.today()  # Download data first before running!
    mapper.plot(plot_date, 'WOOD')
