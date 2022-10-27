"""
Load and parse Excel data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger

from arrow import now
from pandas import DataFrame
from pandas import read_csv


def read_csv_dataframe(filepath_or_buffer: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=filepath_or_buffer)
    return result_df


DATA_FOLDER = './data/'
INPUT_FILE = 'annual-number-of-deaths-by-cause.csv'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    input_file = DATA_FOLDER + INPUT_FILE
    df = read_csv_dataframe(filepath_or_buffer=input_file)
    LOGGER.info('loaded %d rows from %s', len(df), input_file)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
