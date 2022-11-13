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
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from pandas import DataFrame
from pandas import read_excel
from scipy.stats import linregress
from seaborn import lineplot
from seaborn import lmplot
from seaborn import regplot
from seaborn import scatterplot
from seaborn import set_style


def make_plots(column_name: str, column_short_name: str, input_df: DataFrame, fname_short: str,
               scale: Optional[int] = 1) -> float:
    work_df = input_df[['Year', column_name, ]].copy(deep=True)
    work_df['Year'] = work_df['Year'].astype(int)
    work_df.rename(columns={column_name: column_short_name}, inplace=True)
    scale = 1 if scale == 1 else scale
    work_df[column_short_name] = scale * work_df[column_short_name]
    figure_, axes_ = subplots()
    _ = lineplot(ax=axes_, data=work_df, x='Year', y=column_short_name)
    fname_ = '{}{}_lineplot.png'.format(OUTPUT_FOLDER, fname_short)
    savefig(format='png', fname=fname_, )
    close(fig=figure_)
    figure_, axes_ = subplots()
    _ = scatterplot(ax=axes_, data=work_df, x='Year', y=column_short_name)
    fname_ = '{}{}_scatterplot.png'.format(OUTPUT_FOLDER, fname_short)
    savefig(format='png', fname=fname_, )
    close(fig=figure_)
    figure_, axes_ = subplots()
    _ = lmplot(data=work_df, line_kws={'color': 'orange'}, x='Year', y=column_short_name, )
    fname_ = '{}{}_lmplot.png'.format(OUTPUT_FOLDER, fname_short)
    savefig(format='png', fname=fname_, )
    close(fig=figure_)
    figure_, axes_ = subplots()
    _ = regplot(data=work_df, line_kws={'color': 'orange'}, x='Year', y=column_short_name, )
    fname_ = '{}{}_regplot.png'.format(OUTPUT_FOLDER, fname_short)
    savefig(format='png', fname=fname_, )
    close(fig=figure_)
    rvalue = linregress(x=work_df['Year'], y=work_df[column_short_name]).rvalue
    return rvalue * rvalue


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
    df = read_excel_dataframe(io=data_file, header=16, usecols=COLUMNS)
    LOGGER.info('loaded %d rows from %s', len(df), data_file)

    regions_df = df[df['Type'] == 'Region'][['Year', 'Region, subregion, country or area *',
                                             'Natural Change, Births minus Deaths (thousands)',
                                             'Rate of Natural Change (per 1,000 population)',
                                             'Crude Death Rate (deaths per 1,000 population)',
                                             ]].rename(columns={
        'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
        'Region, subregion, country or area *': 'Region',
    })
    regions_df['Region'] = regions_df['Region'].replace({'LATIN AMERICA AND THE CARIBBEAN': 'LATIN AMERICA'})
    set_style(style=SEABORN_STYLE)

    figure_, axes_ = subplots()
    _ = lineplot(ax=axes_, data=regions_df, x='Year', y='Crude Death', hue='Region')
    fname_ = '{}{}_lineplot.png'.format(OUTPUT_FOLDER, 'region_crude_death')
    savefig(format='png', fname=fname_, )
    close(fig=figure_)

    LOGGER.info(df['Type'].value_counts().to_dict())

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
