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
from matplotlib.pyplot import legend
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from pandas import read_excel
from scipy.stats import linregress
from seaborn import lineplot
from seaborn import lmplot
from seaborn import regplot
from seaborn import scatterplot
from seaborn import set_style

from common import COLUMNS


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


DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
SAVE_WORLD_DATA = False
SEABORN_STYLE = 'darkgrid'
# USECOLS = [
#     'Year',
# ]
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
         'Natural Change, Births minus Deaths (thousands)',
         'Rate of Natural Change (per 1,000 population)',
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
    t0 = df[df['Parent code'] == 904]['Location code'].unique()
    t1 = df[df['Parent code'].isin(t0)]['Location code'].unique()

    # Let's try extracting some volatility measures
    deviations = {region: latin_america_df[latin_america_df['Region'] == region]['Crude Death'].std() for region in
                  latin_america_df['Region'].unique()}
    deviation_df = DataFrame(data = {'Region': list(deviations.keys()), 'stddev': list(deviations.values()) })
    maxes = {region: latin_america_df[latin_america_df['Region'] == region]['Crude Death'].max() for region in
             latin_america_df['Region'].unique()}
    max_df = DataFrame(data={'Region': list(maxes.keys()), 'max_value': list(maxes.values()) })
    ranges = dict()
    for region in latin_america_df['Region'].unique():
        region_df = latin_america_df[latin_america_df['Region'] == region]
        ranges[region] = region_df['Crude Death'].max() - region_df['Crude Death'].min()
    range_df = DataFrame(data={'Region': list(ranges.keys()), 'range': list(ranges.values()) })

    for code in []:  # t0:
        region_df = df[(df['Parent code'] == code) | (df['Location code'] == code)][
            ['Year', 'Region, subregion, country or area *', 'Location code',
             'Natural Change, Births minus Deaths (thousands)',
             'Rate of Natural Change (per 1,000 population)',
             'Crude Death Rate (deaths per 1,000 population)',
             ]].rename(columns={
            'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
            'Region, subregion, country or area *': 'Region',
        })

        codes = region_df['Location code'].unique()
        for start in range(0, len(codes), 5):
            current = codes[start:start + 5]
            plot_df = region_df[region_df['Location code'].isin(current)]

            figure_lineplot, axes_lineplot = subplots()
            result_lineplot = lineplot(data=plot_df, x='Year', y='Crude Death', hue='Region', )
            legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
            tight_layout()

            name = region_df[region_df['Location code'] == code]['Region'].unique()[0].lower().replace(' ', '_')
            name_png = '{}_{}.png'.format(name, start)
            LOGGER.info('saving plot for code %d to %s', code, name_png)

            savefig(fname=OUTPUT_FOLDER + name_png, format='png')
            close(fig=figure_lineplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
