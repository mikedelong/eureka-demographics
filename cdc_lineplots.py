"""
Load and parse CSV data from the CDC
"""
from json import load
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
from pandas import concat
from pandas import melt
from pandas import read_csv
from seaborn import lineplot
from seaborn import set_style


def read_url_csv(url: str, usecols: list) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, usecols=usecols)
    return result_df


CAUSE_MAP_FILE = 'causes_map.json'
COLUMNS = ['ICD-10 113 Cause List', 'ICD-10 113 Cause List Code', 'Year', 'Deaths', 'Population', 'crude rate',
           'log10 deaths']
DATA_FOLDER = './data/'
FIGSIZE = (10, 7)
INPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
MAKE_PLOTS = True
OTHER_DATA_FOLDER = './data_cdc/'
OUTPUT_FOLDER = './plot_cdc/'
PLOT_SIZE = 9
SEABORN_STYLE = 'darkgrid'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OTHER_DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    cause_map_file = OTHER_DATA_FOLDER + CAUSE_MAP_FILE
    with open(file=cause_map_file, mode='r') as input_fp:
        CAUSES_MAP = load(fp=input_fp)
    input_file = DATA_FOLDER + INPUT_FILE

    df = read_url_csv(url=input_file, usecols=COLUMNS[:4]).rename(columns={COLUMNS[1]: 'Code'})
    # we need to touch up the original DataFrame by adding a zero value for COVID for 2019
    # otherwise our line plots don't capture COVID
    covid_df = df[df['Code'] == 'GR113-137'].copy(deep=True)
    covid_df['Year'] = 2019
    covid_df['Deaths'] = 0
    df = concat([df, covid_df])

    # rank by the most recent year
    max_year = df['Year'].max()
    # build the max year ranks if we want to rank by the most recent year
    max_year_deaths = '{} Deaths'.format(max_year)
    max_year_df = df[df['Year'] == max_year][[COLUMNS[0], 'Code', 'Deaths']].reset_index().rename(
        columns={'Deaths': max_year_deaths}).drop(columns=['index'])
    max_year_df['rank'] = max_year_df[max_year_deaths].rank(ascending=False)

    # choose which DataFrame to use for the ranking
    major_causes = [item for item in df[COLUMNS[0]].unique().tolist() if item.startswith('#')]
    major_causes_df = max_year_df[max_year_df[COLUMNS[0]].isin(major_causes)].sort_values(by=['rank'], ascending=True)
    major_causes_ranked = major_causes_df['Code'].values

    if MAKE_PLOTS:
        set_style(style=SEABORN_STYLE)
        # let's do the major causes together
        for start in range(0, len(major_causes_ranked), PLOT_SIZE):
            # swap l_var and r_var to get curves labeled by their code
            l_var, r_var = 'Code', COLUMNS[0]
            plot_df = melt(
                frame=df[df['Code'].isin(major_causes_ranked[start:start + PLOT_SIZE])].drop(columns=[l_var]),
                id_vars=['Year', r_var], value_name='Deaths!', ).drop(columns=['variable']).rename(
                columns={'Deaths!': 'Deaths'})
            if r_var == COLUMNS[0]:
                plot_df['Cause'] = plot_df[COLUMNS[0]].apply(lambda x: CAUSES_MAP[x][:30])

            figure, axes = subplots(figsize=FIGSIZE)
            plot_result = lineplot(ax=axes, data=plot_df, estimator=None,
                                   x='Year', y='Deaths', hue=[COLUMNS[0], 'Cause'][1])
            fname = '{}{}_{}_lineplot.png'.format(OUTPUT_FOLDER, 'cdc_113', start)
            plot_result.get_legend().set_bbox_to_anchor((1, 1))
            tight_layout()
            savefig(format='png', fname=fname, )
            close(fig=figure)
            LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
