"""
Load Project HAL data and build a graph
"""

from datetime import date
from logging import INFO
from logging import basicConfig
from logging import getLogger

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import title
from pandas import DataFrame
from pandas import read_excel
from seaborn import histplot


def get_excel_dataframe(io: str) -> DataFrame:
    result_df = read_excel(io=io)
    return result_df


FIGSIZE = (16, 9)
INPUT_FILE = './data/HAL/HAL.XLS'
URL = 'http://people.uncw.edu/hinese/HAL/HAL.zip'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    df = get_excel_dataframe(io=INPUT_FILE)
    df = df[df['Year'] != '1900s']
    df = df[df['Mo'] != '.']
    df = df[df['Day'] != '.']
    column = 'month-date'
    df[column] = df.apply(axis=1, func=lambda x: date(year=int(x['Year']), month=int(x['Mo']), day=15))
    # we want monthly buckets
    min_date = df[column].min()
    max_date = df[column].max()
    bins = 2 * (max_date.year - min_date.year)
    figure, axes = subplots(figsize=FIGSIZE)
    result = histplot(ax=axes, bins=bins, data=df[(min_date < df[column]) & (df[column] < max_date)], discrete=False,
                      element='bars', kde=True, stat='count', x=column, )
    title('source: {}'.format(URL))
    savefig(format='png', fname='./project_hal.png')
    close(fig=figure)

    # get the year data
    columns = {'index': 'Year', 'Year': 'Deaths'}
    years_df = df['Year'].value_counts().to_frame().reset_index(level=0).rename(columns=columns).sort_values(by='Year')

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
