"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from typing import Optional
from typing import Union

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from pandas import DataFrame
from pandas import melt
from pandas import read_excel
from seaborn import relplot
from seaborn import set_style


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


COLUMNS = ['Index', 'Variant', 'Region, subregion, country or area *', 'Notes',
           'Location code', 'ISO3 Alpha-code', 'ISO2 Alpha-code', 'SDMX code**',
           'Type', 'Parent code', 'Year',
           'Total Population, as of 1 January (thousands)',
           'Total Population, as of 1 July (thousands)',
           'Male Population, as of 1 July (thousands)',
           'Female Population, as of 1 July (thousands)',
           'Population Density, as of 1 July (persons per square km)',
           'Population Sex Ratio, as of 1 July (males per 100 females)',
           'Median Age, as of 1 July (years)',
           'Natural Change, Births minus Deaths (thousands)',
           'Rate of Natural Change (per 1,000 population)',
           'Population Change (thousands)', 'Population Growth Rate (percentage)',
           'Population Annual Doubling Time (years)', 'Births (thousands)',
           'Births by women aged 15 to 19 (thousands)',
           'Crude Birth Rate (births per 1,000 population)',
           'Total Fertility Rate (live births per woman)',
           'Net Reproduction Rate (surviving daughters per woman)',
           'Mean Age Childbearing (years)',
           'Sex Ratio at Birth (males per 100 female births)',
           'Total Deaths (thousands)', 'Male Deaths (thousands)',
           'Female Deaths (thousands)',
           'Crude Death Rate (deaths per 1,000 population)',
           'Life Expectancy at Birth, both sexes (years)',
           'Male Life Expectancy at Birth (years)',
           'Female Life Expectancy at Birth (years)',
           'Life Expectancy at Age 15, both sexes (years)',
           'Male Life Expectancy at Age 15 (years)',
           'Female Life Expectancy at Age 15 (years)',
           'Life Expectancy at Age 65, both sexes (years)',
           'Male Life Expectancy at Age 65 (years)',
           'Female Life Expectancy at Age 65 (years)',
           'Life Expectancy at Age 80, both sexes (years)',
           'Male Life Expectancy at Age 80 (years)',
           'Female Life Expectancy at Age 80 (years)',
           'Infant Deaths, under age 1 (thousands)',
           'Infant Mortality Rate (infant deaths per 1,000 live births)',
           'Live Births Surviving to Age 1 (thousands)',
           'Under-Five Deaths, under age 5 (thousands)',
           'Under-Five Mortality (deaths under age 5 per 1,000 live births)',
           'Mortality before Age 40, both sexes (deaths under age 40 per 1,000 live births)',
           'Male Mortality before Age 40 (deaths under age 40 per 1,000 male live births)',
           'Female Mortality before Age 40 (deaths under age 40 per 1,000 female live births)',
           'Mortality before Age 60, both sexes (deaths under age 60 per 1,000 live births)',
           'Male Mortality before Age 60 (deaths under age 60 per 1,000 male live births)',
           'Female Mortality before Age 60 (deaths under age 60 per 1,000 female live births)',
           'Mortality between Age 15 and 50, both sexes (deaths under age 50 per 1,000 alive at age 15)',
           'Male Mortality between Age 15 and 50 (deaths under age 50 per 1,000 males alive at age 15)',
           'Female Mortality between Age 15 and 50 (deaths under age 50 per 1,000 females alive at age 15)',
           'Mortality between Age 15 and 60, both sexes (deaths under age 60 per 1,000 alive at age 15)',
           'Male Mortality between Age 15 and 60 (deaths under age 60 per 1,000 males alive at age 15)',
           'Female Mortality between Age 15 and 60 (deaths under age 60 per 1,000 females alive at age 15)',
           'Net Number of Migrants (thousands)',
           'Net Migration Rate (per 1,000 population)']
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
SAVE_WORLD_DATA = False
SEABORN_STYLE = 'darkgrid'
USECOLS = [
    'Crude Birth Rate (births per 1,000 population)',
    'Crude Death Rate (deaths per 1,000 population)',
    'Population Change (thousands)',
    'Population Growth Rate (percentage)',
    'Rate of Natural Change (per 1,000 population)',
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

    data_file = DATA_FOLDER + INPUT_FILE
    df = read_excel_dataframe(io=data_file, header=16, usecols=USECOLS)
    LOGGER.info('loaded %d rows from %s', len(df), data_file)
    # filter for the data we want and make a copy because we need to add columns
    world_df = df[df['Region, subregion, country or area *'] == 'WORLD'].copy(deep=True)

    set_style(style=SEABORN_STYLE)

    birth_death_df = world_df[['Year',
                               'Crude Birth Rate (births per 1,000 population)',
                               'Crude Death Rate (deaths per 1,000 population)',
                               ]].rename(columns={
        'Crude Birth Rate (births per 1,000 population)': 'Births',
        'Crude Death Rate (deaths per 1,000 population)': 'Deaths',
    })
    plot_df = melt(frame=birth_death_df, id_vars=['Year'], value_name='Rate', value_vars=['Births', 'Deaths'])

    figure_relplot, axes_relplot = subplots()
    result_relplot = relplot(col='variable', data=plot_df, kind='line', x='Year', y='Rate', )
    savefig(fname=OUTPUT_FOLDER + 'birth_death_relplot.png', format='png')
    close(fig=figure_relplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
