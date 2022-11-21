"""
Load Excel data and write CSV
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from pandas import DataFrame

from arrow import now

from common import COLUMNS
from common import read_excel_dataframe

DATA_FOLDER = './data/'
DROP_COLUMNS = ['Index', 'Variant', 'Notes', 'ISO3 Alpha-code', 'ISO2 Alpha-code', 'SDMX code**', ]
INPUT_FILE = 'WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx'
OUTPUT_FOLDER = './data/'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    data_file = DATA_FOLDER + INPUT_FILE
    df = read_excel_dataframe(io=data_file, header=16, usecols=COLUMNS)
    LOGGER.info('loaded %d rows from %s', len(df), data_file)

    df = df.drop(columns=DROP_COLUMNS)
    df = df[df['Type'] != 'Label/Separator']
    df['Year'] = df['Year'].astype(int)
    path_or_buffer = OUTPUT_FOLDER + INPUT_FILE.replace('.xlsx', '.csv')
    LOGGER.info('writing %d rows to %s', len(df), path_or_buffer)
    df.to_csv(path_or_buf=path_or_buffer, index=False)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
