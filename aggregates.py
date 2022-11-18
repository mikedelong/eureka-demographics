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
REGION_SUBREGION = {'World', 'Region', 'Subregion', }
RENAME_COLUMNS = {'Crude Death Rate (deaths per 1,000 population)': 'Crude Death',
                  'Region, subregion, country or area *': 'Aggregate', }
SAVE_WORLD_DATA = False
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

    codes_df = df[['Region, subregion, country or area *', 'Type', 'Parent code', 'Location code']].drop_duplicates()
    codes_df = codes_df[codes_df['Type'].isin(REGION_SUBREGION)]
    # map the regions' parent codes onto their location codes
    codes_df['Parent code'] = codes_df.apply(axis=1,
                                             func=lambda x: x['Location code'] if x['Type'] == 'Region' else x[
                                                 'Parent code'])
    # discard all the countries, areas, labels, and separators
    aggregate_df = df[df['Type'].isin(REGION_SUBREGION)][AGGREGATE_COLUMNS].rename(columns=RENAME_COLUMNS)
    codes_df = codes_df.rename(columns=RENAME_COLUMNS)

    aggregate = ['Aggregate']
    x_var = 'Mean Crude Death'
    y_var = 'std dev Crude Death'
    plot_df = aggregate_df.groupby(by=aggregate).mean().rename(columns={'Crude Death': x_var}).merge(
        right=aggregate_df.groupby(by=aggregate).std().rename(columns={'Crude Death': y_var}),
        on=aggregate).reset_index()

    # merge/join in the parent codes so we can use them for the hues below
    plot_df = plot_df.merge(right=codes_df, on='Aggregate')

    set_style(style=SEABORN_STYLE)
    figure_scatterplot, axes_scatterplot = subplots()
    hue = 'Parent code'
    result_scatterplot = lmplot(data=plot_df, x=x_var, y=y_var, fit_reg=False, hue=hue, legend=False, aspect=2, )
    label_point(x=plot_df[x_var], y=plot_df[y_var], val=plot_df['Aggregate'], ax=gca())
    tight_layout()
    savefig(fname=OUTPUT_FOLDER + 'aggregate_mean_stddev_scatterplot.png', format='png')
    close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
