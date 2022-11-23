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
    result_df = read_csv(filepath_or_buffer=url,)
    return result_df

DATA_FOLDER = './data/'
INPUT_FILE = 'bi63-dtpu-rows.csv'
OUTPUT_FOLDER = './plot/'
REFRESH_DATA = False
URL = 'https://data.cdc.gov/api/views/bi63-dtpu/rows.csv?accessType=DOWNLOAD&bom=true&format=true'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    # if we want to refresh then we need to go get the data from the URL and write a local copy
    # otherwise read the data from our local copy
    if REFRESH_DATA:
        df = read_url_csv(url=URL)
        output_file = DATA_FOLDER + INPUT_FILE
        df.to_csv(path_or_buf=output_file, index=False)
    else:
        input_file = DATA_FOLDER + INPUT_FILE
        df = read_url_csv(url=input_file)

    LOGGER.info(df.shape)


    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
