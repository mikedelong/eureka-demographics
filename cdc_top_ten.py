"""
Load and parse CSV data from the CDC
"""
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
from pandas import read_csv
from seaborn import histplot
from seaborn import set_style
from pandas import Series
from pandas import concat


def read_url_csv(url: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, thousands=',')
    return result_df


CAUSES = ['Unintentional injuries', 'All causes', 'Alzheimer\'s disease', 'Stroke', 'CLRD', 'Diabetes', 'Heart disease',
          'Influenza and pneumonia', 'Suicide', 'Cancer', 'Kidney disease']
COLORMAP = 'tab20'
DATA_FOLDER = './data/'
FIGSIZE = (12, 9)
INPUT_FILE = 'bi63-dtpu-rows.csv'
OUTPUT_FOLDER = './plot/'
REFRESH_DATA = False
SEABORN_STYLE = 'darkgrid'
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

    us_df = df[df['State'] == 'United States'].copy(deep=True)
    us_df.plot.bar(stacked=True)

    us_df['Deaths'] = us_df['Deaths'].astype(int)
    us_df['Year'] = us_df['Year'].astype(int)
    us_df = us_df.drop(columns=['113 Cause Name', 'State', 'Age-adjusted Death Rate'])
    # figure out the Other deaths
    all_causes_df = us_df[us_df['Cause Name'] == 'All causes'].drop(columns=['Cause Name'])
    top_ten_df = us_df[us_df['Cause Name'] != 'All causes']
    top_ten_df = top_ten_df.drop(columns=['Cause Name']).groupby(by=['Year'], axis=0).sum().reset_index()
    all_causes_dict = Series(all_causes_df['Deaths'].values, index=all_causes_df['Year'].values).to_dict()
    top_ten_dict = Series(top_ten_df['Deaths'].values, index=top_ten_df['Year'].values).to_dict()
    other_dict = {year: all_causes_dict[year] - top_ten_dict[year] for year in all_causes_dict.keys()}
    other_df = DataFrame(data={'Year': list(other_dict.keys()), 'Cause Name': ['Other'] * len(other_dict),
                               'Deaths': list(other_dict.values())})

    us_df = concat([us_df[us_df['Cause Name'] != 'All causes'], other_df])

    set_style(style=SEABORN_STYLE)
    figure, axes = subplots(figsize=FIGSIZE)
    plot_result = histplot(ax=axes,
                           bins=us_df['Year'].max() - us_df['Year'].min() + 1, data=us_df, hue='Cause Name',
                           multiple='stack', shrink=0.8, weights='Deaths', x='Year', )
    # Fix the legend so it's not on top of the bars.
    plot_result.get_legend().set_bbox_to_anchor((1, 1))
    tight_layout()
    fname = '{}{}_stacked_bar.png'.format(OUTPUT_FOLDER, 'us_top_ten')
    savefig(format='png', fname=fname, )
    close(fig=figure)
    LOGGER.info('saved plot in %s', fname)

    # now do an area plot
    plot_df = us_df[['Year', 'Deaths', 'Cause Name']].pivot(index='Year', values='Deaths', columns='Cause Name')
    # we need to put the columns in a particular order to get a nice-looking plot
    totals = {column: plot_df[column].sum() for column in plot_df.columns.tolist()}
    totals = sorted([(key, value) for key, value in totals.items()], key=lambda x: x[1], reverse=True)
    order = [item[0] for item in totals]
    order = [item for item in order if item != 'Other'] + ['Other']
    plot_df = plot_df[order]
    figure, axes = subplots(figsize=FIGSIZE)
    # we need to supply a colormap to keep from repeating colors
    plot_result = plot_df.plot.area(ax=axes, colormap=COLORMAP)
    plot_result.get_legend().set_bbox_to_anchor((1, 1))
    axes.set_xticks(ticks=plot_df.index)
    tight_layout()
    fname = '{}{}_stacked_area.png'.format(OUTPUT_FOLDER, 'us_top_ten')
    savefig(format='png', fname=fname, )
    close(fig=figure)
    LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
