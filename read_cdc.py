"""
Load and parse CSV data from the CDC
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import log10
from pathlib import Path

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import gca
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from pandas import read_csv
from seaborn import lmplot

from common import label_point


def read_url_csv(url: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, thousands=',', sep='\t')
    return result_df


DATA_FOLDER = './data/'
INPUT_FILE = 'Underlying Cause of Death, 1999-2020.txt'
OUTPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
OUTPUT_FOLDER = './plot_cdc/'
SCALING = 1000

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    input_file = DATA_FOLDER + INPUT_FILE
    df = read_url_csv(url=input_file)
    df = df.drop(columns=['Notes', 'Year Code', 'Crude Rate']).dropna()
    for column in ['Year', 'Deaths', 'Population']:
        df[column] = df[column].astype(int)
    df['crude rate'] = SCALING * df['Deaths'] / df['Population']
    df['log10 deaths'] = df['Deaths'].apply(log10)

    output_file = DATA_FOLDER + OUTPUT_FILE
    LOGGER.info('writing %d rows to %s', len(df), output_file)
    df.to_csv(path_or_buf=output_file, index=False)

    # let's start building our scatterplot
    column = 'ICD-10 113 Cause List Code'
    mean = 'mean Deaths'
    y_var = 'std dev Deaths'
    mean_df = df[[column, 'Deaths']].groupby(by=[column]).mean().reset_index().rename(columns={'Deaths': mean})
    std_df = df[[column, 'Deaths']].groupby(by=[column]).std().reset_index().rename(columns={'Deaths': y_var})
    plot_df = DataFrame(mean_df).merge(right=std_df, how='inner', on=column).fillna(0)

    figure_scatterplot, axes_scatterplot = subplots()
    result_scatterplot = lmplot(data=plot_df, x=mean, y=y_var, fit_reg=False, legend=False, aspect=2, )
    label_point(x=plot_df[mean], y=plot_df[y_var], val=plot_df[column], ax=gca())
    tight_layout()
    savefig(fname=OUTPUT_FOLDER + 'cdc_113_scatterplot.png', format='png')
    close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
