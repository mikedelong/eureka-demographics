"""
Load and parse HTML data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from typing import Optional

from arrow import now
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from pandas import DataFrame
from pandas import read_html


def get_html_dataframe(url: str, skiprows: Optional[int]) -> list[DataFrame]:
    result_df = read_html(io=url, skiprows=skiprows)
    return result_df


URL = 'http://law2.umkc.edu/faculty/projects/ftrials/shipp/lynchingyear.html'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    df = get_html_dataframe(url=URL, skiprows=3)
    df = df[0].dropna().iloc[0:87]
    for column in df.columns:
        df[column] = df[column].astype(int)
    df['Year'] = df['Year'].astype(int)

    fig, ax = subplots(figsize=(16, 9))
    ax.stackplot(df['Year'].values, df['Whites'].values, df['Blacks'].values, labels=['White', 'Black'])
    ax.legend(loc='upper left')
    savefig(fname='./umkc_lynchings.png', format='png')

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
