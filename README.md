# ETF-Loader
ETF-Loader is a Python library for downloading ETF composition data. So far this has been implemented for iShares ETFs.

## Usage
Downloading ETF compositions:
```python
from etf_mapper import ISharesLoader

br_loader = ISharesLoader()
br_loader.download_compositions_of_country('us')
```

Mapping regional information of an ETF by ticker:
```python
from etf_mapper import CompoMapper
import datetime as dt

mapper = CompoMapper()
plot_date = dt.date.today()  # Download data first before running!
mapper.plot(plot_date, 'WOOD')

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)