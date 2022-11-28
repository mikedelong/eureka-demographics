"""
Load and parse CSV data from the CDC
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from math import log10
from pathlib import Path

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import gca
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import tight_layout
from pandas import DataFrame
from pandas import Series
from pandas import read_csv
from seaborn import lmplot

from common import label_point


def read_url_csv(url: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, thousands=',', sep='\t')
    return result_df


ASPECT = 1.6
DATA_FOLDER = './data/'
INPUT_FILE = 'Underlying Cause of Death, 1999-2020.txt'
MAP_LABELS = {
    'GR113-018': 'Other and unspecified infectious and parasitic diseases',
    'GR113-019': 'Malignant neoplasms',
    'GR113-027': 'Malignant neoplasms of trachea, bronchus and lung',
    'GR113-053': 'Major cardiovascular diseases',
    'GR113-054': 'Diseases of heart',
    'GR113-058': 'Ischemic heart diseases',
    'GR113-059': 'Acute myocardial infarction',
    'GR113-061': 'Other forms of chronic ischemic heart disease',
    'GR113-063': 'All other forms of chronic ischemic heart disease',
    'GR113-086': 'Other chronic lower respiratory diseases',
    'GR113-111': 'All other diseases (Residual)',
    'GR113-122': 'Accidental poisoning and exposure to noxious substances',
    'GR113-137': 'COVID-19',
}
OUTPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
OUTPUT_FOLDER = './plot_cdc/'
REPLACE_LABELS = {'018', '019', '027', '053', '054', '058', '059', '061', '063', '086', '111', '122', '137'}
SCALING = 1000

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    input_file = DATA_FOLDER + INPUT_FILE
    df = read_url_csv(url=input_file)
    df = df.drop(columns=['Notes', 'Year Code', 'Crude Rate']).dropna()
    for column in ['Year', 'Deaths', 'Population']:
        df[column] = df[column].astype(int)
    df['crude rate'] = SCALING * df['Deaths'] / df['Population']
    df['log10 deaths'] = df['Deaths'].apply(log10)

    output_file = DATA_FOLDER + OUTPUT_FILE
    LOGGER.info('writing %d rows to %s', len(df), output_file)
    df.to_csv(path_or_buf=output_file, index=False)

    # let's start building our scatterplot
    columns = ['ICD-10 113 Cause List Code', 'ICD-10 113 Cause List']
    column = columns[0]
    name_dict = Series(df[columns[1]].values, index=df[columns[0]]).to_dict()
    replace_labels = {'GR113-{}'.format(item): name_dict['GR113-{}'.format(item)] for item in REPLACE_LABELS}

    mean = 'mean Deaths'
    mean_df = df[[column, 'Deaths']].groupby(by=[column]).mean().reset_index().rename(columns={'Deaths': mean})
    total = 'total Deaths'
    total_df = df[[column, 'Deaths']].groupby(by=[column]).sum().reset_index().rename(columns={'Deaths': total})
    y_var = 'std dev Deaths'
    std_df = df[[column, 'Deaths']].groupby(by=[column]).std().reset_index().rename(columns={'Deaths': y_var})
    x_var = [mean, total][0]
    plot_df = (total_df if x_var in {total} else mean_df).merge(right=std_df, how='inner', on=column).fillna(0)
    plot_df['label'] = plot_df[column].apply(func=lambda x: MAP_LABELS[x] if x in MAP_LABELS.keys() else x)

    figure_scatterplot, axes_scatterplot = subplots()
    result_scatterplot = lmplot(data=plot_df, x=x_var, y=y_var, fit_reg=False, legend=False, aspect=ASPECT, )
    label_point(x=plot_df[x_var], y=plot_df[y_var], val=plot_df['label'], ax=gca())
    tight_layout()
    savefig(fname=OUTPUT_FOLDER + 'cdc_113_scatterplot.png', format='png')
    close(fig=figure_scatterplot)
    del axes_scatterplot
    del result_scatterplot

    # cut away the large values so we can see the inner, smaller results
    plot_df = plot_df[(plot_df[mean] < 200000) & (plot_df[y_var] < 20000)]
    figure_scatterplot, axes_scatterplot = subplots()
    result_scatterplot = lmplot(data=plot_df, x=x_var, y=y_var, fit_reg=False, legend=False, aspect=ASPECT, )
    label_point(x=plot_df[x_var], y=plot_df[y_var], val=plot_df['label'], ax=gca())
    tight_layout()
    savefig(fname=OUTPUT_FOLDER + 'cdc_113_small_scatterplot.png', format='png')
    close(fig=figure_scatterplot)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
