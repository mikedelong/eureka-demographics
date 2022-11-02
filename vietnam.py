"""
Load and parse HTML data
"""
from collections import Counter
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
from pandas import read_csv
from seaborn import histplot


def get_csv_dataframe(filepath_or_buffer: str, names: list[str]) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=filepath_or_buffer, low_memory=False, names=names, sep='|', )
    return result_df

FIGSIZE = (16, 9)
INPUT_FILE = './data/DCAS.VN.EXT08.DAT'
NAMES = ['Service Number', 'Component Code', 'Person Type Name Code', 'Person Type Name', 'Member Name',
         'Member Service Code', 'Member Service Name', 'Rank Rate', 'Pay Grade', 'Occupation Code',
         'Occupation Name', 'Birth Date', 'Gender', 'Home of Record City', 'Home of Record County',
         'Home of Record Country Code', 'Home of Record State Code', 'State or Province Name', 'Marital Name',
         'Religion Short Name', 'Religion Code', 'Race Name', 'Ethnic Short Name', 'Race OMB Name',
         'Ethnic Group Name', 'Casualty Circumstances', 'Casualty City', 'Casualty State or Province Code',
         'Casualty Country/Over Water Code', 'Region Name', 'Country/Over Water Name', 'Unit', 'Duty Code',
         'Process Date', 'Incident or Death Date', 'Year', 'War or Conflict Code',
         'Operation Incident Type Code', 'Operation/Incident Name', 'Location Name', 'Closure Date',
         'Aircraft Type', 'Hostile/Non-Hostile Death Indicator', 'Casualty Type Name', 'Casualty Category Name',
         'Incident Casualty Reason Name', 'Casualty Category Short Name', 'Remains Recovered',
         'Casualty Closure Name', 'Vietnam Wall Row and Panel Indicator', 'Incident Casualty Category Name',
         'Incident Casualty Category Date', 'Incident Casualty Category Short Name',
         'Incident Hostile or Incident Non-Hostile Death', 'Incident Aircraft Type']
REFRESH = False
URL = 'https://catalog.archives.gov/OpaAPI/media/2240992/content/arcmedia/electronic-records/rg-330/dcase/' \
      'DCAS.VN.EXT08.DAT?download=true'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    counts = Counter(NAMES)
    df = get_csv_dataframe(filepath_or_buffer=URL, names=NAMES) if REFRESH else get_csv_dataframe(
        filepath_or_buffer=INPUT_FILE, names=NAMES)

    date_columns = ['Process Date', 'Birth Date', 'Incident or Death Date', ]
    for column in date_columns:
        df[column] = df[column].apply(lambda x: date(year=x // 10000, month=(x // 100) % 100, day=x % 100))

    # filter out extreme data
    min_date = date(year=1963, month=1, day=1)
    max_date = date(year=1974, month=1, day=1)
    column = 'Incident or Death Date'
    # we want monthly buckets
    bins = 12 * (max_date.year - min_date.year)
    figure, axes = subplots(figsize=FIGSIZE)
    result = histplot(ax=axes, bins=bins, data=df[(min_date < df[column]) & (df[column] < max_date)], discrete=False,
                      element='bars', kde=False, stat='count', x=column, )
    title('source: {}'.format(URL))
    savefig(format='png', fname='./vietnam.png')
    close(fig=figure)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
