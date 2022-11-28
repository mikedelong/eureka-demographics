"""
Load and parse CSV data from the CDC
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from pandas import melt
from pandas import read_csv
from seaborn import lineplot


def read_url_csv(url: str, usecols: list) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, usecols=usecols)
    return result_df


COLUMNS = ['ICD-10 113 Cause List', 'ICD-10 113 Cause List Code', 'Year', 'Deaths', 'Population', 'crude rate',
           'log10 deaths']
DATA_FOLDER = './data/'
INPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
OUTPUT_FOLDER = './plot_cdc/'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    input_file = DATA_FOLDER + INPUT_FILE


    df = read_url_csv(url=input_file, usecols=[COLUMNS[0],
                                               COLUMNS[1], 'Year', 'Deaths', ]).rename(
        columns={'ICD-10 113 Cause List Code' : 'Code'}
    )
    major_df = df[~df[COLUMNS[0]].str.contains('#')]
    minor_df = df[df[COLUMNS[0]].str.contains('#')]
    codes = df['Code'].unique()
    # df = df[df['Code'].isin(codes[:10])]
    plot_df = melt(frame=minor_df.drop(columns=[COLUMNS[0]]), id_vars=['Year', 'Code'], value_name='Deaths', ).drop(columns=['variable'])

    figure_, axes_ = subplots()
    _ = lineplot(ax=axes_, data=plot_df, x='Year', y='Deaths', hue='Code')
    fname = '{}{}_lineplot.png'.format(OUTPUT_FOLDER, 'cdc_113')
    tight_layout()
    savefig(format='png', fname=fname, )
    close(fig=figure_)
    LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
