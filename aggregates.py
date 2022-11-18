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


# todo move to common
# https://stackoverflow.com/questions/46027653/adding-labels-in-x-y-scatter-plot-with-seaborn
def label_point(x, y, val, ax):
    rows_df = concat({'x': x, 'y': y, 'value': val}, axis=1)
    for i, point in rows_df.iterrows():
        ax.text(point['x'] + 0.03, point['y'] + 0.01, str(point['value']), fontsize='x-small')


def read_excel_dataframe(io: str, header: int, usecols: Optional[Union[list, int]]) -> DataFrame:
    result_df = read_excel(engine='openpyxl', header=header, io=io, usecols=usecols)
    return result_df


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

    # discard all the countries, areas, labels, and separators
    columns = ['Region, subregion, country or area *',
               'Crude Death Rate (deaths per 1,000 population)']
    rename_columns = {
        'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
        'Region, subregion, country or area *': 'Aggregate',
    }
    types = {
        'World', 'SDG region', 'Development Group',
        'Special other', 'Income Group', 'Region', 'Subregion',
    }

    region_subregion = {
        'World',
        # 'SDG region',
        # 'Development Group',
        # 'Special other', 'Income Group',
        'Region', 'Subregion',
    }
    aggregate_df = df[df['Type'].isin(region_subregion)][columns].rename(columns=rename_columns)

    columns = ['Aggregate']
    x_var = 'Mean Crude Death'
    y_var = 'std dev Crude Death'
    plot_df = aggregate_df.groupby(by=columns).mean().rename(columns={'Crude Death': x_var}).merge(
        right=aggregate_df.groupby(by=columns).std().rename(columns={'Crude Death': y_var}), on=columns).reset_index()

    set_style(style=SEABORN_STYLE)

    figure_scatterplot, axes_scatterplot = subplots()
    result_scatterplot = lmplot(data=plot_df, x=x_var, y=y_var, fit_reg=False,
                                # hue='hue',
                                legend=False, aspect=2, )
    label_point(x=plot_df[x_var], y=plot_df[y_var], val=plot_df['Aggregate'], ax=gca())
    tight_layout()
    savefig(fname=OUTPUT_FOLDER + 'aggregate_mean_stddev_scatterplot.png', format='png')
    close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
