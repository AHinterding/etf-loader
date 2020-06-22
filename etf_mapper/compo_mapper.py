import datetime as dt
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from loguru import logger


class CompoMapper(object):
    """
    Class to map and plot the previously downloaded ETF composition.

    """

    def __init__(self):
        self.logger = logger

    @logger.catch(reraise=True)
    def load_etf_compo(self, file_path: Path) -> pd.DataFrame:
        """
        Loads the composition file of an ETF.

        Args:
            file_path (Path): The compositions file path.

        Returns:
            pd.DataFrame: The ETF composition, including ISO 3166-1 codes for each constituent.

        """

        if not file_path.exists():
            error_msg = f'Non-existent file path {file_path}! Data must be downloaded first!'
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        compo_frame = pd.read_csv(file_path, index_col=0)
        compo_frame = compo_frame[compo_frame['Asset Class'] == 'Equity'].copy()
        compo_frame['Weight (%)'] = compo_frame['Weight (%)'].apply(lambda x: float(x))
        compo_frame['iso2_code'] = compo_frame['ISIN'].apply(lambda x: x[:2])
        compo_frame['iso3_code'] = compo_frame['iso2_code'].apply(lambda x: self.get_iso3_from_iso2(x))
        compo_frame.dropna(inplace=True)

        return compo_frame

    def get_file_path_by_ticker(self, plot_date: dt.date, ticker: str) -> Path:
        """
        Mapping the ticker to the respective ETF composition file path.

        Args:
            plot_date (dt.date): The download date for the composition
            ticker (str): The ETF ticker.

        Returns:
            Path: The path to the composition file.

        """

        self.logger.debug(f'Sampling file path for {ticker}.')
        downloads_folder = Path('downloads') / 'compositions' / str(plot_date)
        file_name = f'{ticker}_holdings_{plot_date}.csv'

        full_file_path = downloads_folder / file_name

        return full_file_path

    def get_country_weights(self, file_path: Path) -> pd.DataFrame:
        """
        Calculates the constituents weights and logarithmic weights for an ETF composition.

        Args:
            file_path (Path): The ETF composition file path.

        Returns:
            pd.DataFrame: The extended composition, now including calculated weightings.

        """

        self.logger.debug(f'Loading the country weights for {file_path.name}.')
        compo_frame = self.load_etf_compo(file_path)
        compo_frame_grouped = compo_frame.groupby('iso3_code').sum()
        iso_frame = self.load_iso_mapping()
        country_weights = pd.DataFrame(data=iso_frame['Alpha-3 code'].values,
                                       index=iso_frame['Alpha-3 code'],
                                       columns=['iso3_code'])
        country_weights['weight'] = 0

        for iso3 in compo_frame_grouped.index:
            country_weights.loc[iso3, 'weight'] = compo_frame_grouped.loc[iso3, 'Weight (%)']

        country_weights.reset_index(inplace=True, drop=True)
        country_weights['country'] = country_weights['iso3_code'].apply(lambda x: self.get_country_name_from_iso3(x))
        country_weights.loc[:, 'weight log'] = country_weights['weight'].apply(lambda x: np.log(x))

        return country_weights

    @lru_cache()
    def load_iso_mapping(self) -> pd.DataFrame:
        """
        Load the mapping for ISO 3166-1 alpha-2 and alpha-3 codes of countries.

        Returns:
            pd.DataFrame: A frame that contains all country information.

        """

        self.logger.debug(f'Loading ISO mapping.')
        file_path = Path('data') / 'iso_country_mapping.csv'
        iso_frame = pd.read_csv(file_path)
        iso_frame['Alpha-2 code'] = iso_frame['Alpha-2 code'].apply(lambda x: x.replace(' ', '')).copy()
        iso_frame['Alpha-3 code'] = iso_frame['Alpha-3 code'].apply(lambda x: x.replace(' ', '')).copy()

        return iso_frame

    def get_country_name_from_iso3(self, iso3: str) -> str:
        """
        Gets the country name based on the ISO 3166-1 alpha-3 code.

        Args:
            iso3 (str): The alpha-3 code to map.

        Returns:
            str: The respective country.

        """

        iso_frame = self.load_iso_mapping()
        if iso3 in iso_frame['Alpha-3 code'].values:
            target_idx = list(iso_frame['Alpha-3 code']).index(iso3)
            country = iso_frame['Name'][target_idx]
        else:
            warning_msg = f'No valid ISO mapping found for {iso3}!'
            self.logger.warning(warning_msg)
            country = None

        return country

    def get_iso3_from_iso2(self, iso2: str) -> str:
        """
        Returns the alpha-3 code from a given alpha-2 code.

        Args:
            iso2: The alpha-2 code.

        Returns:
            str: The alpha-3 code.

        """

        iso_frame = self.load_iso_mapping()
        if iso2 in iso_frame['Alpha-2 code'].values:
            target_idx = list(iso_frame['Alpha-2 code']).index(iso2)
            iso3_str = iso_frame['Alpha-3 code'][target_idx]
        else:
            warning_msg = f'No valid ISO mapping found for {iso2}!'
            self.logger.warning(warning_msg)
            iso3_str = None

        return iso3_str

    @logger.catch()
    def plot(self, plot_date: dt.date, ticker: str) -> None:
        """
        Plots the composition of an ETF as specified by the ETF ticker.

        Args:
            plot_date (dt.date): The download date for the composition
            ticker: The ETF ticker.

        """

        compo_path = self.get_file_path_by_ticker(plot_date, ticker)
        weights = self.get_country_weights(compo_path)
        self.show_weightings_plot(weights)

    @staticmethod
    def show_weightings_plot(weights: pd.DataFrame) -> None:
        """
        Plots the weights on a per-country basis.

        Args:
            weights: The constituent weights of a composition.

        """
        fig = go.Figure(data=go.Choropleth(
            locations=weights['iso3_code'],
            z=weights['weight'],
            colorscale='PuBu',
            autocolorscale=False,
            marker_line_color='lightgray',
            colorbar_title="Country Weight"
        ))

        fig.show()
