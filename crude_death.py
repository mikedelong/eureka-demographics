"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from typing import Optional
from typing import Union

from arrow import now
from pandas import DataFrame
from pandas import read_excel
from seaborn import set_style
from seaborn import FacetGrid
from seaborn import scatterplot
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


CRUDE_DATA_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1_CRUDE_DEATH.xlsx'
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
SAVE_CRUDE_DATA = False
SEABORN_STYLE = 'darkgrid'
USECOLS = [
    'Crude Death Rate (deaths per 1,000 population)',
    'Region, subregion, country or area *',
    'Type',
    'Year',
]

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    crude_data_file = DATA_FOLDER + CRUDE_DATA_FILE
    if SAVE_CRUDE_DATA:
        data_file = DATA_FOLDER + INPUT_FILE
        df = read_excel_dataframe(io=data_file, header=16, usecols=USECOLS)
        LOGGER.info('loaded %d rows from %s', len(df), data_file)
        # filter for the data we want and make a copy because we need to add columns
        crude_df = df[df['Type'].isin(values={'Country/Area', 'World'})].copy(deep=True)
        # add dates for the two total population values
        crude_df.to_excel(crude_data_file)
        LOGGER.info('wrote %d rows to %s', len(crude_df), crude_data_file)
    else:
        crude_df = read_excel_dataframe(io=crude_data_file, header=0, usecols=None)
        LOGGER.info('loaded %d rows from %s', len(crude_df), crude_data_file)

    set_style(style=SEABORN_STYLE)
    crude_df.rename(columns={'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
                             'Region, subregion, country or area *': 'Country'}, inplace=True)
    grid = FacetGrid(col='Country', col_wrap=3, data=crude_df, sharex=True, )
    result = grid.map_dataframe(func=scatterplot, x='Crude Death')
    savefig(fname='./crude_death_grid.png', format='png')

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
