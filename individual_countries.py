"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from typing import Mapping

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from pandas import DataFrame
from pandas import Series
from seaborn import lineplot
from seaborn import set_style

from common import COLUMNS
from common import read_excel_dataframe


def columns_to_dict(input_df: DataFrame, key_column: str, value_column: str) -> Mapping:
    local_df = input_df[[key_column, value_column]].drop_duplicates()
    return Series(local_df[value_column].values, index=local_df[key_column]).to_dict()


AGGREGATE_COLUMNS = ['Year', 'Region, subregion, country or area *', 'Crude Death Rate (deaths per 1,000 population)',
                     'Location code', 'Parent code']
COUNTRIES = {
    'Cambodia': ['Cambodia', 'Viet Nam', 'Laos', 'Thailand'],
    'East Timor': ['East Timor', 'Indonesia'],
    'Iraq': ['Iraq', 'Iran', 'Kuwait', 'Turkey', 'Syria'],
    'North Korea': ['North Korea', 'South Korea', 'Japan'],
    'Rwanda': ['Rwanda', 'Uganda', 'Burundi', 'Tanzania'],
    'South Sudan': ['Ethiopia', 'South Sudan', 'Uganda', 'Kenya'],
    'Vietnam': ['Viet Nam', 'Laos', 'Thailand'],
}
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
RENAME_COLUMNS = {'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
                  'Region, subregion, country or area *': 'Area', }
RENAME_COUNTRIES = {
    'Dem. People\'s Republic of Korea': 'North Korea',
    'Lao People\'s Democratic Republic': 'Laos',
    'Iran (Islamic Republic of)': 'Iran',
    'Türkiye': 'Turkey',
    'Republic of Korea': 'South Korea',
    'Syrian Arab Republic': 'Syria',
    'Timor-Leste': 'East Timor',
    'United Republic of Tanzania': 'Tanzania',
}
SEABORN_STYLE = 'darkgrid'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    data_file = DATA_FOLDER + INPUT_FILE
    df = read_excel_dataframe(io=data_file, header=16, usecols=COLUMNS)
    LOGGER.info('loaded %d rows from %s', len(df), data_file)
    df = df[df['Type'] != 'Label/Separator']
    df = df[df['Region, subregion, country or area *'] != 'Holy See']

    data_df = df[AGGREGATE_COLUMNS].rename(columns=RENAME_COLUMNS)
    data_df['Area'] = data_df['Area'].replace(RENAME_COUNTRIES)
    country_code_dict = columns_to_dict(input_df=data_df, key_column='Area', value_column='Location code')
    parent_code_dict = columns_to_dict(input_df=data_df, key_column='Location code', value_column='Parent code')

    set_style(style=SEABORN_STYLE)
    for public_name, country_values in COUNTRIES.items():
        LOGGER.info('country: %s', public_name)
        # get the country code for each country
        our_country_codes = {country_code_dict[country] for country in country_values}
        for index in range(4):
            our_country_codes |= {parent_code_dict[country] for country in our_country_codes if
                                  country in parent_code_dict.keys()}

        # add the World country code
        our_country_codes |= {900}

        # now we can get the slice of data we need
        plot_df = data_df[data_df['Location code'].isin(our_country_codes)]
        figure_lineplot, axes_lineplot = subplots()
        result_lineplot = lineplot(data=plot_df, x='Year', y='Crude Death', hue='Area', )
        fname = OUTPUT_FOLDER + '{}_cdr_lineplot.png'.format(public_name.replace(' ', '_'))
        LOGGER.info('plot file: %s', fname)
        savefig(fname=fname, format='png')
        close(fig=figure_lineplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
