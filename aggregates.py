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
from seaborn import lmplot
from seaborn import set_style

from common import COLUMNS
from common import label_point
from common import read_excel_dataframe

AGGREGATE_COLUMNS = ['Region, subregion, country or area *', 'Crude Death Rate (deaths per 1,000 population)']
DATA_FOLDER = './data/'
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './plot/'
RENAME_COLUMNS = {'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
                  'Region, subregion, country or area *': 'Aggregate', }
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

    set_style(style=SEABORN_STYLE)
    for index, aggregate in enumerate(
            [{'World', 'Region', 'Subregion', }, {'World', 'Development Group', 'Special other', 'Income Group', },
             {'World', 'Country/Area'}, ]):
        codes_df = df[
            ['Region, subregion, country or area *', 'Type', 'Parent code', 'Location code']].drop_duplicates()
        codes_df = codes_df[codes_df['Type'].isin(aggregate)]
        # map the regions' parent codes onto their location codes
        codes_df['Parent code'] = codes_df.apply(axis=1,
                                                 func=lambda x: x['Location code'] if x['Type'] == 'Region' else x[
                                                     'Parent code'])
        # discard all the countries, areas, labels, and separators
        aggregate_df = df[df['Type'].isin(aggregate)][AGGREGATE_COLUMNS].rename(columns=RENAME_COLUMNS)
        codes_df = codes_df.rename(columns=RENAME_COLUMNS)

        this_column = ['Aggregate']
        x_var = 'Mean Crude Death'
        y_var = 'std dev Crude Death'
        plot_df = aggregate_df.groupby(by=this_column).mean().rename(columns={'Crude Death': x_var}).merge(
            right=aggregate_df.groupby(by=this_column).std().rename(columns={'Crude Death': y_var}),
            on=this_column).reset_index()

        # merge/join in the parent codes so we can use them for the hues below
        plot_df = plot_df.merge(right=codes_df, on=this_column)

        figure_scatterplot, axes_scatterplot = subplots()
        hue = 'Parent code'
        result_scatterplot = lmplot(aspect=1.6, data=plot_df, fit_reg=False, height=6, hue=hue, legend=False, x=x_var,
                                    y=y_var, )
        label_point(x=plot_df[x_var], y=plot_df[y_var], val=plot_df['Aggregate'], ax=gca())
        tight_layout()
        fname = OUTPUT_FOLDER + 'aggregate_mean_stddev_scatterplot_{}.png'.format(index + 1)
        LOGGER.info('saving plot to %s', fname)
        savefig(fname=fname, format='png')
        close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
