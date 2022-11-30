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
MAKE_PLOTS = True
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

    df = read_url_csv(url=input_file, usecols=COLUMNS[:4]).rename(columns={COLUMNS[1]: 'Code'})
    major_df = df[~df[COLUMNS[0]].str.contains('#')]
    minor_df = df[df[COLUMNS[0]].str.contains('#')]
    codes = df['Code'].unique()
    # rank the codes by total count
    total = 'total Deaths'
    total_df = df[[COLUMNS[0], 'Code', 'Deaths']].groupby(by=[COLUMNS[0], 'Code']).sum().reset_index().rename(
        columns={'Deaths': total})
    total_df['rank'] = total_df[total].rank()
    causes_ranked = DataFrame(total_df).sort_values(by=['rank'])['Code'].tolist()

    if MAKE_PLOTS:
        size = 8
        for start in range(0, len(causes_ranked), size):
            # swap l_var and r_var to get curves labeled by their code
            l_var, r_var = 'Code', COLUMNS[0]
            # todo why is this producing a FutureWarning?
            plot_df = melt(frame=df[df['Code'].isin(causes_ranked[start:start + size])].drop(columns=[l_var]),
                           id_vars=['Year', r_var], value_name='Deaths', ).drop(columns=['variable'])
            if r_var == COLUMNS[0]:
                plot_df['Cause'] = plot_df[COLUMNS[0]].apply(lambda x: x[:30])

            figure_, axes_ = subplots()
            hue = [COLUMNS[0], 'Cause'][1]
            _ = lineplot(ax=axes_, data=plot_df, x='Year', y='Deaths', hue=hue)
            fname = '{}{}_{}_lineplot.png'.format(OUTPUT_FOLDER, 'cdc_113', start)
            tight_layout()
            savefig(format='png', fname=fname, )
            close(fig=figure_)
            LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
