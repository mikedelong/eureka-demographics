"""
Load and parse CSV data from the CDC
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path

from arrow import now
from pandas import DataFrame
from pandas import read_csv


def read_url_csv(url: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, thousands=',', sep='\t')
    return result_df

DATA_FOLDER = './data/'
INPUT_FILE = 'Underlying Cause of Death, 1999-2020.txt'
OUTPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
SCALING = 1000

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, ]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    input_file = DATA_FOLDER + INPUT_FILE
    df = read_url_csv(url=input_file)
    df = df.drop(columns=['Notes', 'Year Code', 'Crude Rate']).dropna()
    for column in ['Year', 'Deaths', 'Population']:
        df[column] = df[column].astype(int)
    df['crude rate'] = SCALING * df['Deaths']/df['Population']

    output_file = DATA_FOLDER + OUTPUT_FILE
    LOGGER.info('writing %d rows to %s', len(df), output_file)
    df.to_csv(path_or_buf=output_file, index=False)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
