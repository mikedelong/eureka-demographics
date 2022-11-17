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
from matplotlib.pyplot import gca
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from pandas import concat
from pandas import read_excel
from seaborn import lineplot
from seaborn import lmplot
from seaborn import set_style

from common import COLUMNS


# https://stackoverflow.com/questions/46027653/adding-labels-in-x-y-scatter-plot-with-seaborn
def label_point(x, y, val, ax):
    rows_df = concat({'x': x, 'y': y, 'value': val}, axis=1)
    for i, point in rows_df.iterrows():
        ax.text(point['x'] + 0.03, point['y'] + 0.01, str(point['value']), fontsize='x-small')


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
SAVE_WORLD_DATA = False
SEABORN_STYLE = 'darkgrid'
TO_REPLACE = {'LATIN AMERICA AND THE CARIBBEAN': 'Latin America', 'Bolivia (Plurinational State of)': 'Bolivia',
              'Venezuela (Bolivarian Republic of)': 'Venezuela', 'Saint Martin (French part)': 'Saint Martin',
              'Sint Maarten (Dutch part)': 'Sint Maarten', 'Falkland Islands (Malvinas)': 'Falkland Islands', }
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

    # for Latin America the location code is 904
    latin_america_df = df[(df['Parent code'] == 904) | (df['Location code'] == 904)][
        ['Year', 'Region, subregion, country or area *',
         'Crude Death Rate (deaths per 1,000 population)',
         ]].rename(columns={
        'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
        'Region, subregion, country or area *': 'Region',
    })
    latin_america_df['Region'] = latin_america_df['Region'].replace(
        {'LATIN AMERICA AND THE CARIBBEAN': 'Latin America'})

    set_style(style=SEABORN_STYLE)
    figure_lineplot, axes_lineplot = subplots()
    result_lineplot = lineplot(data=latin_america_df, x='Year', y='Crude Death', hue='Region', )

    savefig(fname=OUTPUT_FOLDER + 'latin_america_lineplot.png', format='png')
    close(fig=figure_lineplot)

    # first get the Asian subregions
    region_codes = df[df['Parent code'] == 904]['Location code'].unique()
    country_codes = df[df['Parent code'].isin(region_codes)]['Location code'].unique()

    countries_df = df[df['Location code'].isin(country_codes)][
        ['Year', 'Region, subregion, country or area *',
         'Crude Death Rate (deaths per 1,000 population)',
         ]].rename(columns={
        'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
        'Region, subregion, country or area *': 'Region',
    })
    # todo is this necessary?
    countries_df['Region'] = countries_df['Region'].replace(
        {'LATIN AMERICA AND THE CARIBBEAN': 'Latin America'})

    # Let's try extracting some volatility measures
    deviations = {region: countries_df[countries_df['Region'] == region]['Crude Death'].std() for region in
                  countries_df['Region'].unique()}
    deviation_df = DataFrame(data={'country': list(deviations.keys()), 'stddev': list(deviations.values())})
    maxes = {region: countries_df[countries_df['Region'] == region]['Crude Death'].max() for region in
             countries_df['Region'].unique()}
    max_df = DataFrame(data={'country': list(maxes.keys()), 'max': list(maxes.values())})
    ranges = dict()
    for country in countries_df['Region'].unique():
        country_df = countries_df[countries_df['Region'] == country]
        ranges[country] = country_df['Crude Death'].max() - country_df['Crude Death'].min()
    range_df = DataFrame(data={'country': list(ranges.keys()), 'range': list(ranges.values())})
    means = {region: countries_df[countries_df['Region'] == region]['Crude Death'].mean() for region in
             countries_df['Region'].unique()}
    mean_df = DataFrame(data={'country': list(means.keys()), 'mean': list(means.values())})

    plot_data = {'max': max_df, 'stddev': deviation_df, 'range': range_df, }
    for y_variable, data_df in plot_data.items():
        plot_df = mean_df.merge(right=data_df, how='inner', on='country')
        plot_df['hue'] = plot_df['mean'] * plot_df[y_variable]
        plot_df['country'].replace(inplace=True, to_replace=TO_REPLACE, )
        mean = 'Mean Crude Death'
        y_var = y_variable + ' Crude Death'
        plot_df.rename(columns={'mean': mean, y_variable: y_var}, inplace=True, )
        figure_scatterplot, axes_scatterplot = subplots()
        result_scatterplot = lmplot(data=plot_df, x=mean, y=y_var, hue='hue', legend=False, aspect=2, )
        label_point(x=plot_df[mean], y=plot_df[y_var], val=plot_df['country'], ax=gca())
        tight_layout()

        savefig(fname=OUTPUT_FOLDER + 'latin_america_mean_{}_scatterplot.png'.format(y_variable), format='png')
        close(fig=figure_scatterplot)

    # plot selected countries vs. the regional rate
    for index, countries in enumerate([
        ['Haiti', 'Montserrat', 'LATIN AMERICA AND THE CARIBBEAN', 'Bolivia (Plurinational State of)',
         'WORLD', 'Falkland Islands (Malvinas)'],
        ['WORLD', 'LATIN AMERICA AND THE CARIBBEAN', 'Mexico', 'Honduras', 'Guatemala', 'Nicaragua'], ]):
        plot_df = df[df['Region, subregion, country or area *'].isin(countries)][
            ['Year', 'Region, subregion, country or area *',
             'Crude Death Rate (deaths per 1,000 population)',
             ]].rename(columns={
            'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
            'Region, subregion, country or area *': 'Region/Country',
        })
        plot_df['Region/Country'].replace(inplace=True, to_replace=TO_REPLACE)
        figure_lineplot, axes_lineplot = subplots()
        result_lineplot = lineplot(data=plot_df, x='Year', y='Crude Death', hue='Region/Country', )
        savefig(fname=OUTPUT_FOLDER + 'latin_america_comparison_lineplot-{}.png'.format(index + 1), format='png')
        close(fig=figure_lineplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
