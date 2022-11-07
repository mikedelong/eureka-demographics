"""
Load and parse Excel data
"""
from datetime import date
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from typing import Optional
from typing import Union

from arrow import now
from pandas import DataFrame
from pandas import read_excel
from plotly.express import scatter
from plotly.io import to_html


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './divs/'
SAVE_WORLD_DATA = False
USECOLS = [
    'Crude Death Rate (deaths per 1,000 population)',
    'Region, subregion, country or area *',
    'Total Deaths (thousands)',
    'Total Population, as of 1 January (thousands)',
    'Total Population, as of 1 July (thousands)',
    'Type',
    'Year',
]
WORLD_DATA_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1_WORLD.xlsx'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    world_file = DATA_FOLDER + WORLD_DATA_FILE
    if Path(world_file).exists():
        # if we don't load the whole data file above then we need to load the world-only data
        usecols = USECOLS + ['January', 'July']
        world_df = read_excel_dataframe(io=world_file, header=0, usecols=usecols)
        LOGGER.info('loaded %d rows from %s', len(world_df), WORLD_DATA_FILE)
    else:
        data_file = DATA_FOLDER + INPUT_FILE
        df = read_excel_dataframe(io=data_file, header=16, usecols=USECOLS)
        LOGGER.info('loaded %d rows from %s', len(df), data_file)
        # filter for the data we want and make a copy because we need to add columns
        world_df = df[df['Region, subregion, country or area *'] == 'WORLD'].copy(deep=True)
        # add dates for the two total population values
        world_df['January'] = world_df['Year'].apply(lambda x: date(year=int(x), month=1, day=1))
        world_df['July'] = world_df['Year'].apply(lambda x: date(year=int(x), month=7, day=1))
        world_file = DATA_FOLDER + WORLD_DATA_FILE
        world_df.to_excel(world_file)
        LOGGER.info('wrote %d rows to %s', len(world_df), WORLD_DATA_FILE)

    # combine the two sets of date/population values
    population = dict(zip(world_df['January'], world_df['Total Population, as of 1 January (thousands)'])) | dict(
        zip(world_df['July'], world_df['Total Population, as of 1 July (thousands)']))
    # build the population DataFrame
    population_df = DataFrame(
        data={'date': list(population.keys()), 'population': list(population.values())}).sort_values(
        by='date').reset_index(drop=True)
    population_df['population'] = 1000 * population_df['population']
    with open(file=OUTPUT_FOLDER + 'world_population.scatter.txt', mode='w') as output_fp:
        output_fp.write(to_html(fig=scatter(data_frame=population_df, x='date', y='population'), full_html=False))

    LOGGER.info('saved population plot')

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
