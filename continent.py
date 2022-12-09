"""
Load and parse Excel data
"""

from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import gca
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from seaborn import lineplot
from seaborn import lmplot
from seaborn import set_style

from common import COLUMNS
from common import label_point
from common import read_excel_dataframe

CONTINENT_DATA = {
    'africa': 903,
    'asia': 935,
    'europe': 908,
    'latin america': 904,
    'north america': 905,
    'oceania': 909,
}
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot_crude/'
SAVE_WORLD_DATA = False
SEABORN_STYLE = 'darkgrid'
TO_REPLACE = {'LATIN AMERICA AND THE CARIBBEAN': 'Latin America', 'Bolivia (Plurinational State of)': 'Bolivia',
              'Venezuela (Bolivarian Republic of)': 'Venezuela', 'Saint Martin (French part)': 'Saint Martin',
              'Sint Maarten (Dutch part)': 'Sint Maarten', 'Falkland Islands (Malvinas)': 'Falkland Islands', }

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
    df = df.drop(columns=['Index'])
    df = df[df['Region, subregion, country or area *'] != 'Holy See']

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
    figure_regions, axes_regions = subplots()
    result_regions = lineplot(ax=axes_regions, data=regions_df, x='Year', y='Crude Death', hue='Region')
    fname_regions = '{}{}_lineplot.png'.format(OUTPUT_FOLDER, 'region_crude_death')
    LOGGER.info('writing to %s', fname_regions)
    savefig(format='png', fname=fname_regions, )
    close(fig=figure_regions)

    for continent, location_code in CONTINENT_DATA.items():
        region_codes = df[df['Parent code'] == location_code]['Location code'].unique()
        country_codes = df[df['Parent code'].isin(region_codes)][
            'Location code'].unique() if continent != 'north america' else region_codes

        regions_df = df[(df['Location code'].isin(region_codes)) | (df['Location code'] == location_code)][
            ['Year', 'Region, subregion, country or area *',
             'Crude Death Rate (deaths per 1,000 population)',
             ]].rename(columns={
            'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
            'Region, subregion, country or area *': 'Region',
        })

        figure_lineplot, axes_lineplot = subplots()
        result_lineplot = lineplot(data=regions_df, x='Year', y='Crude Death', hue='Region', )
        fname_lineplot = OUTPUT_FOLDER + '{}_lineplot.png'.format(continent.replace(' ', '_'))
        LOGGER.info('writing to %s', fname_lineplot)
        savefig(fname=fname_lineplot, format='png')
        close(fig=figure_lineplot)

        countries_df = df[df['Location code'].isin(country_codes)][
            ['Year', 'Region, subregion, country or area *',
             'Crude Death Rate (deaths per 1,000 population)',
             ]].rename(columns={
            'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
            'Region, subregion, country or area *': 'Region',
        })
        deviations = {region: countries_df[countries_df['Region'] == region]['Crude Death'].std() for region in
                      countries_df['Region'].unique()}
        deviation_df = DataFrame(data={'country': list(deviations.keys()), 'std dev': list(deviations.values())})
        means = {region: countries_df[countries_df['Region'] == region]['Crude Death'].mean() for region in
                 countries_df['Region'].unique()}
        mean_df = DataFrame(data={'country': list(means.keys()), 'mean': list(means.values())})
        plot_df = mean_df.merge(right=deviation_df, how='inner', on='country')
        stddev = 'std dev'
        plot_df['hue'] = plot_df['mean'] * plot_df[stddev]
        plot_df['country'].replace(inplace=True, to_replace=TO_REPLACE, )
        mean = 'Mean Crude Death'
        y_var = stddev + ' Crude Death'
        plot_df.rename(columns={'mean': mean, stddev: y_var}, inplace=True, )
        figure_scatterplot, axes_scatterplot = subplots()
        result_scatterplot = lmplot(data=plot_df, x=mean, y=y_var, hue='hue', legend=False, aspect=2, )
        label_point(x=plot_df[mean], y=plot_df[y_var], val=plot_df['country'], ax=gca())
        tight_layout()
        fname_scatterplot = OUTPUT_FOLDER + '{}_mean_{}_scatterplot.png'.format(continent.replace(' ', '_'),
                                                                                stddev.replace(' ', '_'))
        LOGGER.info('writing to %s', fname_scatterplot)
        savefig(fname=fname_scatterplot, format='png')
        close(fig=figure_scatterplot)

        subregion_df = df[df['Parent code'] == location_code][[
            'Year', 'Region, subregion, country or area *',
            'Parent code',
            'Natural Change, Births minus Deaths (thousands)',
            'Rate of Natural Change (per 1,000 population)',
            'Crude Death Rate (deaths per 1,000 population)',
        ]].rename(columns={
            'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
            'Region, subregion, country or area *': 'Region',
        })
        del axes_lineplot
        del figure_lineplot
        del result_lineplot
        figure_lineplot, axes_lineplot = subplots()
        result_lineplot = lineplot(ax=axes_lineplot, data=subregion_df, x='Year', y='Crude Death', hue='Region')
        fname_lineplot = '{}{}_subregion_lineplot.png'.format(OUTPUT_FOLDER, continent.replace(' ', '_'), )
        LOGGER.info('writing to %s', fname_lineplot)
        savefig(format='png', fname=fname_lineplot, )
        close(fig=figure_lineplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
