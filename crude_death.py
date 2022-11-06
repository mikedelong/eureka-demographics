"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from os.path import exists
from pathlib import Path
from typing import Optional
from typing import Union

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from numpy import dot
from pandas import DataFrame
from pandas import read_excel
from seaborn import lineplot
from seaborn import scatterplot
from seaborn import set_style


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


COUNTRIES = ['Afghanistan', 'Albania', 'China', 'Ethiopia', 'Ireland', 'Russian Federation', 'Rwanda', 'Somalia',
             'United States of America', 'Viet Nam', ]
CRUDE_DATA_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1_CRUDE_DEATH.xlsx'
DATA_FOLDER = './data/'
DO_ALL_GRAPHS = False
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot_crude/'
SAVE_CRUDE_DATA = False
SEABORN_STYLE = 'darkgrid'
USECOLS = [
    'Crude Death Rate (deaths per 1,000 population)', 'Region, subregion, country or area *', 'Type', 'Year', ]

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    # todo download original file if it ddoes not exist

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

    crude_df.rename(columns={'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
                             'Region, subregion, country or area *': 'Country'}, inplace=True)

    world_ = crude_df[crude_df['Country'] == 'WORLD']['Crude Death'].values
    dot_world = dot(a=world_, b=world_)
    correlations = {country: dot(a=crude_df[crude_df['Country'] == country]['Crude Death'].values, b=world_) / dot_world
                    for country in crude_df['Country'].unique() if country not in {'Holy See', 'WORLD'}}
    correlations_df = DataFrame(data={'country': list(correlations.keys()),
                                      'correlation': list(correlations.values())}).sort_values(by='correlation')
    # todo break this up into multiple readable subplots
    set_style(style=SEABORN_STYLE)
    figure_correlations, axes_correlations = subplots(figsize=(9, 16))
    plot_correlations = scatterplot(data=correlations_df.iloc[0:50], y='country', x='correlation')
    savefig(fname=OUTPUT_FOLDER + 'crude_death_correlations.png', format='png')
    close(fig=figure_correlations)

    # graph a country against the baseline
    for country in crude_df['Country'].unique():
        fname = OUTPUT_FOLDER + '{}-vs-{}.png'.format(country, 'World')
        if exists(fname):
            LOGGER.warning('not creating %s because it already exists.', fname)
        elif country == 'Holy See':
            LOGGER.warning('skipping %s because its data is broken or something', country)
        elif country == 'WORLD':
            LOGGER.warning('skipping %s because it is redundant', country)
        else:
            # todo add a plot with a regression fit line?
            LOGGER.info('line plotting crude rate %s vs world', country)
            graph_df = crude_df[(crude_df['Country'] == 'WORLD') | (crude_df['Country'] == country)]
            figure_lineplot, axes_lineplot = subplots(figsize=(9, 16))
            lineplot_result = lineplot(ax=axes_lineplot, data=graph_df, x='Year', y='Crude Death', hue='Country')
            savefig(format='png', fname=fname, )
            close(fig=figure_lineplot)

    if DO_ALL_GRAPHS:
        for index, country in enumerate(crude_df['Country'].unique()):
            figure, axes = subplots()
            LOGGER.info(country)
            # todo plot these against the world aggregate
            plot_result = scatterplot(ax=axes, data=crude_df[crude_df['Country'] == country], x='Year', y='Crude Death')
            savefig(fname='./plot/{}_crude_death.png'.format(country), format='png')
            close(fig=figure)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
