"""
Load and parse CSV data representing US cause of death data
"""
from logging import INFO
from logging import basicConfig
from logging import getLogger

from arrow import now
from pandas import DataFrame
from pandas import read_csv
from plotly.express import line

from common import reshape


def read_csv_dataframe(filepath_or_buffer: str) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=filepath_or_buffer)
    return result_df


COLUMNS = ['Entity', 'Code', 'Year', 'Number of executions (Amnesty International)',
           'Deaths - Meningitis - Sex: Both - Age: All Ages (Number)',
           "Deaths - Alzheimer's disease and other dementias - Sex: Both - Age: All Ages (Number)",
           "Deaths - Parkinson's disease - Sex: Both - Age: All Ages (Number)",
           'Deaths - Nutritional deficiencies - Sex: Both - Age: All Ages (Number)',
           'Deaths - Malaria - Sex: Both - Age: All Ages (Number)',
           'Deaths - Drowning - Sex: Both - Age: All Ages (Number)',
           'Deaths - Interpersonal violence - Sex: Both - Age: All Ages (Number)',
           'Deaths - Maternal disorders - Sex: Both - Age: All Ages (Number)',
           'Deaths - HIV/AIDS - Sex: Both - Age: All Ages (Number)',
           'Deaths - Drug use disorders - Sex: Both - Age: All Ages (Number)',
           'Deaths - Tuberculosis - Sex: Both - Age: All Ages (Number)',
           'Deaths - Cardiovascular diseases - Sex: Both - Age: All Ages (Number)',
           'Deaths - Lower respiratory infections - Sex: Both - Age: All Ages (Number)',
           'Deaths - Neonatal disorders - Sex: Both - Age: All Ages (Number)',
           'Deaths - Alcohol use disorders - Sex: Both - Age: All Ages (Number)',
           'Deaths - Self-harm - Sex: Both - Age: All Ages (Number)',
           'Deaths - Exposure to forces of nature - Sex: Both - Age: All Ages (Number)',
           'Deaths - Diarrheal diseases - Sex: Both - Age: All Ages (Number)',
           'Deaths - Environmental heat and cold exposure - Sex: Both - Age: All Ages (Number)',
           'Deaths - Neoplasms - Sex: Both - Age: All Ages (Number)',
           'Deaths - Conflict and terrorism - Sex: Both - Age: All Ages (Number)',
           'Deaths - Diabetes mellitus - Sex: Both - Age: All Ages (Number)',
           'Deaths - Chronic kidney disease - Sex: Both - Age: All Ages (Number)',
           'Deaths - Poisonings - Sex: Both - Age: All Ages (Number)',
           'Deaths - Protein-energy malnutrition - Sex: Both - Age: All Ages (Number)', 'Terrorism (deaths)',
           'Deaths - Road injuries - Sex: Both - Age: All Ages (Number)',
           'Deaths - Chronic respiratory diseases - Sex: Both - Age: All Ages (Number)',
           'Deaths - Cirrhosis and other chronic liver diseases - Sex: Both - Age: All Ages (Number)',
           'Deaths - Digestive diseases - Sex: Both - Age: All Ages (Number)',
           'Deaths - Fire, heat, and hot substances - Sex: Both - Age: All Ages (Number)',
           'Deaths - Acute hepatitis - Sex: Both - Age: All Ages (Number)']
DATA_FOLDER = './data/'
INPUT_FILE = 'annual-number-of-deaths-by-cause.csv'
PLOT_FOLDER = './plot_cause_of_death/'
URL = 'https://ourworldindata.org/causes-of-death'

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    input_file = DATA_FOLDER + INPUT_FILE
    df = read_csv_dataframe(filepath_or_buffer=input_file)
    LOGGER.info('loaded %d rows from %s', len(df), input_file)

    # extract the data for just the USA, make the year the index
    usa_df = df[df['Code'] == 'USA'].drop(columns=['Entity', 'Code'])
    usa_df = usa_df.sort_values(by=['Year']).set_index(keys=['Year'])
    # clean up the cause names
    for column in list(usa_df):
        new_column = column.replace(' - Sex: Both - Age: All Ages (Number)', '')
        new_column = new_column.replace('Deaths - ', '')
        usa_df.rename(inplace=True, columns={column: new_column})

    usa_df = df[df['Code'] == 'USA'].drop(columns=['Entity', 'Code'])
    usa_df = usa_df.sort_values(by=['Year']).fillna(value=0)
    for column in list(usa_df):
        new_column = column.replace(' - Sex: Both - Age: All Ages (Number)', '')
        new_column = new_column.replace('Deaths - ', '')
        usa_df.rename(inplace=True, columns={column: new_column})
    usa_df.rename(inplace=True, columns={'Number of executions (Amnesty International)': 'Executions'})

    # let's drop a couple of great big columns before we proceed
    for column in usa_df.columns:
        usa_df[column] = usa_df[column].astype(int)
    # order the columns by their total deaths, most to least
    total_deaths = {column: usa_df[column].sum() for column in usa_df.columns if column != 'Year'}
    total_deaths = sorted([(key, value) for key, value in total_deaths.items()], key=lambda x: x[1], reverse=True)
    total_deaths = [item[0] for item in total_deaths]
    usa_df = usa_df[['Year'] + total_deaths]
    usa_lineplot_df = reshape(input_df=usa_df, x_column='Year', y_columns=total_deaths,
                              y_column_name='Cause', value_column_name='Deaths')

    figure_plotly = line(data_frame=usa_lineplot_df, x='Year', y='Deaths', color='Cause')
    figure_plotly.write_html(PLOT_FOLDER + 'usa_cause_of_death_lineplot.html', )

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
