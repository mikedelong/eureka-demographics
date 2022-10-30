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
from matplotlib.pyplot import title
from pandas import DataFrame
from pandas import read_html


def get_html_dataframe(url: str, skiprows: Optional[int]) -> list[DataFrame]:
    result_df = read_html(io=url, skiprows=skiprows)
    return result_df


FIGSIZE = (16, 8)
OUTPUT_FOLDER = './plot_lynching/'
URL = 'http://law2.umkc.edu/faculty/projects/ftrials/shipp/lynchingyear.html'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    # todo create output folder if it does not exist

    df = get_html_dataframe(url=URL, skiprows=3)
    df = df[0].dropna().iloc[0:87]
    for column in df.columns:
        df[column] = df[column].astype(int)
    df['Year'] = df['Year'].astype(int)

    fig, ax = subplots(figsize=FIGSIZE)
    ax.stackplot(df['Year'].values, df['Whites'].values, df['Blacks'].values, labels=['White', 'Black'])
    ax.legend(loc='upper right')
    title('source: {}'.format(URL))
    savefig(fname=OUTPUT_FOLDER + 'umkc_lynchings.png', format='png')
    del fig

    df['cumulative_white'] = df['Whites'].cumsum()
    df['cumulative_black'] = df['Blacks'].cumsum()
    fig_cumulative, ax_cumulative = subplots(figsize=FIGSIZE)
    ax_cumulative.stackplot(df['Year'].values,
                            df['cumulative_black'].values,
                            df['cumulative_white'].values,
                            labels=['Black (cumulative)', 'White (cumulative)', ])
    ax_cumulative.legend(loc='upper left')
    title('source: {}'.format(URL))
    savefig(fname=OUTPUT_FOLDER + 'umkc_lynchings_cumsum.png', format='png')
    del fig_cumulative

    window = 5
    df['moving_white'] = df['Whites'].rolling(window=window).mean()
    df['moving_black'] = df['Blacks'].rolling(window=window).mean()
    fig_rolling, ax_rolling = subplots(figsize=FIGSIZE)
    ax_rolling.stackplot(df['Year'].values,
                         df['moving_black'].values,
                         df['moving_white'].values,
                         labels=['Black ({}y moving avg)'.format(window), 'White ({}y moving avg)'.format(window), ])
    ax_rolling.legend(loc='upper left')
    title('source: {}'.format(URL))
    savefig(fname=OUTPUT_FOLDER + 'umkc_lynchings_rolling.png', format='png')

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
