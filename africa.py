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

AFRICA_LOCATION_CODE = 903
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
SAVE_WORLD_DATA = False
SEABORN_STYLE = 'darkgrid'
TO_REPLACE = {}

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

    # Africa is Location code 903
    region_codes = df[df['Parent code'] == AFRICA_LOCATION_CODE]['Location code'].unique()
    country_codes = df[df['Parent code'].isin(region_codes)]['Location code'].unique()

    regions_df = df[(df['Location code'].isin(region_codes)) | (df['Location code'] == AFRICA_LOCATION_CODE)][
        ['Year', 'Region, subregion, country or area *',
         'Crude Death Rate (deaths per 1,000 population)',
         ]].rename(columns={
        'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
        'Region, subregion, country or area *': 'Region',
    })

    set_style(style=SEABORN_STYLE)
    figure_lineplot, axes_lineplot = subplots()
    result_lineplot = lineplot(data=regions_df, x='Year', y='Crude Death', hue='Region', )
    savefig(fname=OUTPUT_FOLDER + 'africa_regions_lineplot.png', format='png')
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
    savefig(fname=OUTPUT_FOLDER + 'africa_mean_{}_scatterplot.png'.format(stddev), format='png')
    close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
