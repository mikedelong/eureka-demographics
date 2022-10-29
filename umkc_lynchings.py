"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from typing import Optional

from arrow import now
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
    df = df[0].dropna().iloc[0:88]

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
