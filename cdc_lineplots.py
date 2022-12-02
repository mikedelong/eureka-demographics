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


ACCIDENTS = ['Transport accidents (V01-V99,Y85)',
             'Motor vehicle accidents (V02-V04,V09.0,V09.2,V12-V14,V19.0-V19.2,V19.4-V19.6,V20-V79,V80.3-V80.5,V81.0-V81.1,V82.0-V82.1,V83-V86,V87.0-V87.8,V88.0-V88.8,V89.0,V89.2)',
             'Other land transport accidents (V01,V05-V06,V09.1,V09.3-V09.9,V10-V11,V15-V18,V19.3,V19.8-V19.9,V80.0-V80.2,V80.6-V80.9,V81.2-V81.9,V82.2-V82.9,V87.9,V88.9,V89.1,V89.3,V89.9)',
             'Water, air and space, and other and unspecified transport accidents and their sequelae (V90-V99,Y85)',
             'Nontransport accidents (W00-X59,Y86)',
             'Falls (W00-W19)',
             'Accidental discharge of firearms (W32-W34)',
             'Accidental drowning and submersion (W65-W74)',
             'Accidental exposure to smoke, fire and flames (X00-X09)',
             'Accidental poisoning and exposure to noxious substances (X40-X49)',
             'Other and unspecified nontransport accidents and their sequelae (W20-W31,W35-W64,W75-W99,X10-X39,X50-X59,Y86)']
ASSAULT = ['Intentional self-harm (suicide) by discharge of firearms (X72-X74)',
           'Intentional self-harm (suicide) by other and unspecified means and their sequelae (*U03,X60-X71,X75-X84,Y87.0)',
           'Assault (homicide) by discharge of firearms (*U01.4,X93-X95)',
           'Assault (homicide) by other and unspecified means and their sequelae (*U01.0-*U01.3,*U01.5-*U01.9,*U02,X85-X92,X96-Y09,Y87.1)',
           'Events of undetermined intent (Y10-Y34,Y87.2,Y89.9)',
           'Discharge of firearms, undetermined intent (Y22-Y24)',
           'Other and unspecified events of undetermined intent and their sequelae (Y10-Y21,Y25-Y34,Y87.2,Y89.9)', ]
CAUSE_MAP_FILE = 'causes_map.json'
COLUMNS = ['ICD-10 113 Cause List', 'ICD-10 113 Cause List Code', 'Year', 'Deaths', 'Population', 'crude rate',
           'log10 deaths']
DATA_FOLDER = './data/'
FIGSIZE = (10, 7)
HEART_DISEASE = [
    'Acute rheumatic fever and chronic rheumatic heart diseases (I00-I09)',
    'Hypertensive heart disease (I11)',
    'Hypertensive heart and renal disease (I13)',
    'Ischemic heart diseases (I20-I25)',
    'Acute myocardial infarction (I21-I22)',
    'Other acute ischemic heart diseases (I24)',
    'Other forms of chronic ischemic heart disease (I20,I25)',
    'Atherosclerotic cardiovascular disease, so described (I25.0)',
    'All other forms of chronic ischemic heart disease (I20,I25.1-I25.9)',
    'Other heart diseases (I26-I51)',
    'Acute and subacute endocarditis (I33)',
    'Diseases of pericardium and acute myocarditis (I30-I31,I40)',
    'Heart failure (I50)',
    'All other forms of heart disease (I26-I28,I34-I38,I42-I49,I51)',
]
INPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
MAKE_PLOTS = True
NEOPLASMS = {
    'Malignant neoplasms of lip, oral cavity and pharynx (C00-C14)',
    'Malignant neoplasm of esophagus (C15)',
    'Malignant neoplasm of stomach (C16)',
    'Malignant neoplasms of colon, rectum and anus (C18-C21)',
    'Malignant neoplasms of liver and intrahepatic bile ducts (C22)',
    'Malignant neoplasm of pancreas (C25)',
    'Malignant neoplasm of larynx (C32)',
    'Malignant neoplasms of trachea, bronchus and lung (C33-C34)',
    'Malignant melanoma of skin (C43)',
    'Malignant neoplasm of breast (C50)',
    'Malignant neoplasm of cervix uteri (C53)',
    'Malignant neoplasms of corpus uteri and uterus, part unspecified (C54-C55)',
    'Malignant neoplasm of ovary (C56)',
    'Malignant neoplasm of prostate (C61)',
    'Malignant neoplasms of kidney and renal pelvis (C64-C65)',
    'Malignant neoplasm of bladder (C67)',
    'Malignant neoplasms of meninges, brain and other parts of central nervous system (C70-C72)',
    'Malignant neoplasms of lymphoid, hematopoietic and related tissue (C81-C96)',
    'Hodgkin disease (C81)',
    'Non-Hodgkin lymphoma (C82-C85)',
    'Leukemia (C91-C95)',
    'Multiple myeloma and immunoproliferative neoplasms (C88,C90)',
    'Other and unspecified malignant neoplasms of lymphoid, hematopoietic and related tissue (C96)',
    'All other and unspecified malignant neoplasms (C17,C23-C24,C26-C31,C37-C41,C44-C49,C51-C52,C57-C60,C62-C63,C66,C68-C69,C73-C80,C97)',
}
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

        # now do the breakouts
        for target in [(ACCIDENTS, 'accidents'), (ASSAULT, 'suicide_assault_etc'), (HEART_DISEASE, 'heart_disease'),
                       (NEOPLASMS, 'neoplasms'), ]:
            target_df = df[df[COLUMNS[0]].isin(target[0])]
            l_var, r_var = 'Code', COLUMNS[0]
            plot_df = melt(frame=target_df.drop(columns=[l_var]), id_vars=['Year', r_var], value_name='Deaths!', ).drop(
                columns=['variable']).rename(columns={'Deaths!': 'Deaths'})
            if r_var == COLUMNS[0]:
                plot_df['Cause'] = plot_df[COLUMNS[0]].apply(lambda x: CAUSES_MAP[x][:30])

            figure, axes = subplots(figsize=FIGSIZE)
            plot_result = lineplot(ax=axes, data=plot_df, estimator=None,
                                   x='Year', y='Deaths', hue=[COLUMNS[0], 'Cause'][1])
            fname = '{}{}_{}_lineplot.png'.format(OUTPUT_FOLDER, 'cdc_113', target[1])
            plot_result.get_legend().set_bbox_to_anchor((1, 1))
            tight_layout()
            savefig(format='png', fname=fname, )
            close(fig=figure)
            LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
