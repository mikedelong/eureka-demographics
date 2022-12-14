"""
Aggregate lynching data from two sources
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from typing import Optional

from arrow import now
from matplotlib.pyplot import close
from matplotlib.pyplot import savefig
from matplotlib.pyplot import subplots
from matplotlib.pyplot import xticks
from pandas import DataFrame
from pandas import concat
from pandas import read_excel
from pandas import read_html
from plotly.express import bar
from seaborn import barplot
from plotly.io import to_html
from markdown2 import markdown


def get_excel_dataframe(io: str) -> DataFrame:
    result_df = read_excel(io=io)
    return result_df


def get_html_dataframe(url: str, skiprows: Optional[int]) -> list[DataFrame]:
    result_df = read_html(io=url, skiprows=skiprows)
    return result_df


DATA_FOLDER = './data/HAL/'
FIGSIZE = (16, 9)
HAL_FILE = './data/HAL/HAL.XLS'
OUTPUT_FOLDER = './plot_lynching/'
UMKC_URL = 'http://law2.umkc.edu/faculty/projects/ftrials/shipp/lynchingyear.html'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    umkc_df = get_html_dataframe(url=UMKC_URL, skiprows=3)
    umkc_df = umkc_df[0].dropna().iloc[0:87]
    for column in umkc_df.columns:
        umkc_df[column] = umkc_df[column].astype(int)
    umkc_df['Year'] = umkc_df['Year'].astype(int)

    df = get_excel_dataframe(io=HAL_FILE)
    df = df[df['Year'] != '1900s']
    columns = {'index': 'Year', 'Year': 'Deaths'}
    hal_df = df['Year'].value_counts().to_frame().reset_index(level=0).rename(columns=columns).sort_values(by='Year')

    first_df = umkc_df[['Year', 'Total']].rename(columns={'Total': 'Deaths'})
    first_df['Source'] = 'UMKC'
    second_df = hal_df
    second_df['Source'] = 'HAL'
    aggregate_df = concat([first_df, second_df], ignore_index=True)

    # seaborn version
    figure_barplot, axes_barplot = subplots(figsize=FIGSIZE)
    result_barplot = barplot(ax=axes_barplot, data=aggregate_df, hue='Source', x='Year', y='Deaths', )
    axes_barplot.legend(loc='upper right')
    xticks(rotation=90)
    savefig(format='png', fname=OUTPUT_FOLDER + 'aggregate_lynchings_barplot.png')
    close(fig=figure_barplot)

    # plotly version
    plotly_bar = bar(barmode='group', color='Source', data_frame=aggregate_df, x='Year', y='Deaths', )
    plotly_bar.write_html(OUTPUT_FOLDER + 'aggregate_lynchings_bar.html', )

    div = to_html(fig=plotly_bar, full_html=False)
    md_input = ['# Lynching data from two sources \n' +
                'Here is the preamble text.',
                'And here is the footer text.']

    html_result = [markdown(text=item) for item in md_input]

    with open(file=OUTPUT_FOLDER + 'markdown_text_bar.html', mode='w') as output_fp:
        output_fp.write(
            ' '.join([html_result[0], div, html_result[1]])
        )

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
