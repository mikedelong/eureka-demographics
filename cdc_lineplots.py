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
from pandas import melt
from pandas import read_csv
from seaborn import lineplot


def read_url_csv(url: str, usecols: list) -> DataFrame:
    result_df = read_csv(filepath_or_buffer=url, usecols=usecols)
    return result_df


CAUSES_MAP = {'#Salmonella infections (A01-A02)': 'Salmonella',
              '#Shigellosis and amebiasis (A03,A06)': 'Sigelllosis',
              'Certain other intestinal infections (A04,A07-A09)': 'Intestinal infections',
              '#Tuberculosis (A16-A19)': 'Tuberculosis',
              'Respiratory tuberculosis (A16)': 'Respiratory tuberculosis',
              'Other tuberculosis (A17-A19)': 'Non-respiratory tuberculosis',
              '#Whooping cough (A37)': 'Whooping cough',
              '#Meningococcal infection (A39)': 'Meningitis',
              '#Septicemia (A40-A41)': 'Septicemia',
              '#Syphilis (A50-A53)': 'Syphilis',
              '#Arthropod-borne viral encephalitis (A83-A84,A85.2)': 'Arboviral encephalitis',
              '#Viral hepatitis (B15-B19)': 'Viral hepatitis',
              '#Human immunodeficiency virus (HIV) disease (B20-B24)': 'HIV/AIDS',
              '#Malaria (B50-B54)': 'Malaria',
              'Other and unspecified infectious and parasitic diseases and their sequelae (A00,A05,A20-A36,A42-A44,A48-A49,A54-A79,A81-A82,A85.0-A85.1,A85.8,A86-B04,B06-B09,B25-B49,B55-B99,U07.1)': 'Other infectious diseases',
              '#Malignant neoplasms (C00-C97)': 'Cancerous tumors',
              'Malignant neoplasms of lip, oral cavity and pharynx (C00-C14)': 'Oral cancer',
              'Malignant neoplasm of esophagus (C15)': 'Throat cancer',
              'Malignant neoplasm of stomach (C16)': 'Stomach cancer',
              'Malignant neoplasms of colon, rectum and anus (C18-C21)': 'Colorectal cancer',
              'Malignant neoplasms of liver and intrahepatic bile ducts (C22)': 'Liver cancer',
              'Malignant neoplasm of pancreas (C25)': 'Pancreatic cancer',
              'Malignant neoplasm of larynx (C32)': 'Laryngeal cancer',
              'Malignant neoplasms of trachea, bronchus and lung (C33-C34)': 'Lung cancer',
              'Malignant melanoma of skin (C43)': 'Skin cancer',
              'Malignant neoplasm of breast (C50)': 'Breast cancer',
              'Malignant neoplasm of cervix uteri (C53)': 'Cervical cancer',
              'Malignant neoplasms of corpus uteri and uterus, part unspecified (C54-C55)': 'Other cervical cancer',
              'Malignant neoplasm of ovary (C56)': 'Ovarian cancer',
              'Malignant neoplasm of prostate (C61)': 'Protate cancer',
              'Malignant neoplasms of kidney and renal pelvis (C64-C65)': 'Kidney/pelvic cancer',
              'Malignant neoplasm of bladder (C67)': 'Bladder cancer',
              'Malignant neoplasms of meninges, brain and other parts of central nervous system (C70-C72)': 'Brain cancer',
              'Malignant neoplasms of lymphoid, hematopoietic and related tissue (C81-C96)': 'Lymph node cancer',
              'Hodgkin disease (C81)': 'Hodgkin disease',
              'Non-Hodgkin lymphoma (C82-C85)': 'Non-Hodgkin lymphoma',
              'Leukemia (C91-C95)': 'Leukemia',
              'Multiple myeloma and immunoproliferative neoplasms (C88,C90)': 'Multiple myeloma',
              'Other and unspecified malignant neoplasms of lymphoid, hematopoietic and related tissue (C96)': 'Other lymph node cancer',
              'All other and unspecified malignant neoplasms (C17,C23-C24,C26-C31,C37-C41,C44-C49,C51-C52,C57-C60,C62-C63,C66,C68-C69,C73-C80,C97)': 'Other cancer',
              '#In situ neoplasms, benign neoplasms and neoplasms of uncertain or unknown behavior (D00-D48)': 'Misc. neoplasms',
              '#Anemias (D50-D64)': 'Anemia',
              '#Diabetes mellitus (E10-E14)': 'Diabetes',
              '#Nutritional deficiencies (E40-E64)': 'Nutritional deficiencies',
              'Malnutrition (E40-E46)': 'Malnutrition',
              'Other nutritional deficiencies (E50-E64)': 'Other nutritional deficiencies',
              '#Meningitis (G00,G03)': 'Meningitis',
              '#Parkinson disease (G20-G21)': 'Parkinsons',
              '#Alzheimer disease (G30)': 'Alzheimers',
              'Major cardiovascular diseases (I00-I78)': 'Cardiovascular disease',
              '#Diseases of heart (I00-I09,I11,I13,I20-I51)': 'Heart disease',
              'Acute rheumatic fever and chronic rheumatic heart diseases (I00-I09)': 'Rheumatic fever',
              'Hypertensive heart disease (I11)': 'Hypertension',
              'Hypertensive heart and renal disease (I13)': 'Hypertension/renal disease',
              'Ischemic heart diseases (I20-I25)': 'Ischemic heart disease',
              'Acute myocardial infarction (I21-I22)': 'Myocardial infarction',
              'Other acute ischemic heart diseases (I24)': 'Other acute ischemic HD',
              'Other forms of chronic ischemic heart disease (I20,I25)': 'Other chronic ischemic HD',
              'Atherosclerotic cardiovascular disease, so described (I25.0)': 'Atherosclerosis',
              'All other forms of chronic ischemic heart disease (I20,I25.1-I25.9)': 'Other other CIHD',
              'Other heart diseases (I26-I51)': 'Other HD',
              'Acute and subacute endocarditis (I33)': 'Acute endocarditis',
              'Diseases of pericardium and acute myocarditis (I30-I31,I40)': 'Pericaditis/myocarditis',
              'Heart failure (I50)': 'Heart failure',
              'All other forms of heart disease (I26-I28,I34-I38,I42-I49,I51)': 'Other other HD',
              '#Essential hypertension and hypertensive renal disease (I10,I12,I15)': 'Essential hypertension',
              '#Cerebrovascular diseases (I60-I69)': 'Cerebrovascular diseases',
              '#Atherosclerosis (I70)': 'Atherosclerosis',
              'Other diseases of circulatory system (I71-I78)': 'Other circulatory diseases',
              '#Aortic aneurysm and dissection (I71)': 'Aortic aneurysm/dissection',
              'Other diseases of arteries, arterioles and capillaries (I72-I78)': 'Other arterial diseases',
              'Other disorders of circulatory system (I80-I99)': 'Other circulatory disease',
              '#Influenza and pneumonia (J09-J18)': 'Influenza/pneumonia',
              'Influenza (J09-J11)': 'Influenza',
              'Pneumonia (J12-J18)': 'Pneumonia',
              'Other acute lower respiratory infections (J20-J22,U04)': 'Other acute lower respiratory infections',
              '#Acute bronchitis and bronchiolitis (J20-J21)': 'Acute bronchitis',
              'Other and unspecified acute lower respiratory infections (J22,U04)': 'Other/unspecified lower respiratory disease',
              '#Chronic lower respiratory diseases (J40-J47)': 'Chronic lower respiratory diseases',
              'Bronchitis, chronic and unspecified (J40-J42)': 'Bronchitis',
              'Emphysema (J43)': 'Emphysema',
              'Asthma (J45-J46)': 'Asthma',
              'Other chronic lower respiratory diseases (J44,J47)': 'Other chronic lower respiratory diseases',
              '#Pneumoconioses and chemical effects (J60-J66,J68,U07.0)': 'Pneumoconioses',
              '#Pneumonitis due to solids and liquids (J69)': 'Pneumonitis',
              'Other diseases of respiratory system (J00-J06,J30- J39,J67,J70-J98)': 'Other respiratory diseases',
              '#Peptic ulcer (K25-K28)': 'Peptic ulcer',
              '#Diseases of appendix (K35-K38)': 'Appendicitis',
              '#Hernia (K40-K46)': 'Hernia',
              '#Chronic liver disease and cirrhosis (K70,K73-K74)': 'Liver disease',
              'Alcoholic liver disease (K70)': 'Alcholic liver disease',
              'Other chronic liver disease and cirrhosis (K73-K74)': 'Other chronic liver disease',
              '#Cholelithiasis and other disorders of gallbladder (K80-K82)': 'Cholelithiasis',
              '#Nephritis, nephrotic syndrome and nephrosis (N00-N07,N17-N19,N25-N27)': 'Nephritis/nephrosis',
              'Acute and rapidly progressive nephritic and nephrotic syndrome (N00-N01,N04)': 'Acute nephritis/nephrosis',
              'Chronic glomerulonephritis, nephritis and nephropathy not specified as acute or chronic, and renal sclerosis unspecified (N02-N03,N05-N07,N26)': 'Other nephropathy',
              'Renal failure (N17-N19)': 'Renal failure',
              'Other disorders of kidney (N25,N27)': 'Other kidney disorderss',
              '#Infections of kidney (N10-N12,N13.6,N15.1)': 'Kidney infections',
              '#Hyperplasia of prostate (N40)': 'Prostate hyperplasia',
              '#Inflammatory diseases of female pelvic organs (N70-N76)': 'Female inflammatory diseases',
              '#Pregnancy, childbirth and the puerperium (O00-O99)': 'Pregnancy/childbirth',
              'Pregnancy with abortive outcome (O00-O07)': 'Pregnancy/no childbirth',
              'Other complications of pregnancy, childbirth and the puerperium (O10-O99)': 'Other complications of pregnancy',
              '#Certain conditions originating in the perinatal period (P00-P96)': 'Perinatal complications',
              '#Congenital malformations, deformations and chromosomal abnormalities (Q00-Q99)': 'Congenital malformations/chromosomal abnormalities',
              'Symptoms, signs and abnormal clinical and laboratory findings, not elsewhere classified (R00-R99)': 'Abnormal findings not elsewhere classified',
              'All other diseases (Residual) ': 'Residual other diseases',
              '#Accidents (unintentional injuries) (V01-X59,Y85-Y86)': 'Accidents',
              'Transport accidents (V01-V99,Y85)': 'Transport accidents',
              'Motor vehicle accidents (V02-V04,V09.0,V09.2,V12-V14,V19.0-V19.2,V19.4-V19.6,V20-V79,V80.3-V80.5,V81.0-V81.1,V82.0-V82.1,V83-V86,V87.0-V87.8,V88.0-V88.8,V89.0,V89.2)': 'Motor vehicle accidents',
              'Other land transport accidents (V01,V05-V06,V09.1,V09.3-V09.9,V10-V11,V15-V18,V19.3,V19.8-V19.9,V80.0-V80.2,V80.6-V80.9,V81.2-V81.9,V82.2-V82.9,V87.9,V88.9,V89.1,V89.3,V89.9)': 'Other land transport accidents',
              'Water, air and space, and other and unspecified transport accidents and their sequelae (V90-V99,Y85)': 'Water, air and space accidents',
              'Nontransport accidents (W00-X59,Y86)': 'Nontransport accidents',
              'Falls (W00-W19)': 'Falls',
              'Accidental discharge of firearms (W32-W34)': 'Firearm accidents',
              'Accidental drowning and submersion (W65-W74)': 'Drownings',
              'Accidental exposure to smoke, fire and flames (X00-X09)': 'Smoke, fire and flames',
              'Accidental poisoning and exposure to noxious substances (X40-X49)': 'Accidental poisonings',
              'Other and unspecified nontransport accidents and their sequelae (W20-W31,W35-W64,W75-W99,X10-X39,X50-X59,Y86)': 'Other nontransport accidents',
              '#Intentional self-harm (suicide) (*U03,X60-X84,Y87.0)': 'Suicide',
              'Intentional self-harm (suicide) by discharge of firearms (X72-X74)': 'Suicide/firearms',
              'Intentional self-harm (suicide) by other and unspecified means and their sequelae (*U03,X60-X71,X75-X84,Y87.0)': 'Other suicide',
              '#Assault (homicide) (*U01-*U02,X85-Y09,Y87.1)': 'Homicide',
              'Assault (homicide) by discharge of firearms (*U01.4,X93-X95)': 'Homicide/firearms',
              'Assault (homicide) by other and unspecified means and their sequelae (*U01.0-*U01.3,*U01.5-*U01.9,*U02,X85-X92,X96-Y09,Y87.1)': 'Other homicide',
              '#Legal intervention (Y35,Y89.0)': 'Legal intervention',
              'Events of undetermined intent (Y10-Y34,Y87.2,Y89.9)': 'Events of undetermined intent',
              'Discharge of firearms, undetermined intent (Y22-Y24)': 'Discharge of firearms, undetermined intent',
              'Other and unspecified events of undetermined intent and their sequelae (Y10-Y21,Y25-Y34,Y87.2,Y89.9)': 'Other/unspecified events of undetermined intent',
              '#Operations of war and their sequelae (Y36,Y89.1)': 'War',
              '#Complications of medical and surgical care (Y40-Y84,Y88)': 'Medical complications',
              '#Enterocolitis due to Clostridium difficile (A04.7)': 'Enterocolitis',
              '#COVID-19 (U07.1)': 'COVID-19'}


COLUMNS = ['ICD-10 113 Cause List', 'ICD-10 113 Cause List Code', 'Year', 'Deaths', 'Population', 'crude rate',
           'log10 deaths']
DATA_FOLDER = './data/'
INPUT_FILE = 'Wonder-cause-of-death-1999-2020.csv'
MAKE_PLOTS = True
OUTPUT_FOLDER = './plot_cdc/'
PLOT_SIZE = 8

if __name__ == '__main__':
    TIME_START = now()
    LOGGER = getLogger(__name__, )
    basicConfig(format='%(asctime)s : %(name)s : %(levelname)s : %(message)s', level=INFO, )
    LOGGER.info('started')

    for folder in [DATA_FOLDER, OUTPUT_FOLDER]:
        LOGGER.info('creating folder %s if it does not exist', folder)
        Path(folder).mkdir(parents=True, exist_ok=True)

    input_file = DATA_FOLDER + INPUT_FILE

    df = read_url_csv(url=input_file, usecols=COLUMNS[:4]).rename(columns={COLUMNS[1]: 'Code'})
    codes = df['Code'].unique()
    # rank the codes by total count
    total = 'total Deaths'
    total_df = df[[COLUMNS[0], 'Code', 'Deaths']].groupby(by=[COLUMNS[0], 'Code']).sum().reset_index().rename(
        columns={'Deaths': total})
    total_df['rank'] = total_df[total].rank()
    causes_ranked = DataFrame(total_df).sort_values(by=['rank'])['Code'].tolist()

    if MAKE_PLOTS:
        for start in range(0, len(causes_ranked), PLOT_SIZE):
            # swap l_var and r_var to get curves labeled by their code
            l_var, r_var = 'Code', COLUMNS[0]
            # todo why is this producing a FutureWarning?
            plot_df = melt(frame=df[df['Code'].isin(causes_ranked[start:start + PLOT_SIZE])].drop(columns=[l_var]),
                           id_vars=['Year', r_var], value_name='Deaths', ).drop(columns=['variable'])
            if r_var == COLUMNS[0]:
                plot_df['Cause'] = plot_df[COLUMNS[0]].apply(lambda x: CAUSES_MAP[x][:30])

            figure_, axes_ = subplots()
            hue = [COLUMNS[0], 'Cause'][1]
            _ = lineplot(ax=axes_, data=plot_df, x='Year', y='Deaths', hue=hue)
            fname = '{}{}_{}_lineplot.png'.format(OUTPUT_FOLDER, 'cdc_113', start)
            tight_layout()
            savefig(format='png', fname=fname, )
            close(fig=figure_)
            LOGGER.info('saved plot in %s', fname)

    LOGGER.info('total time: {:5.2f}s'.format((now() - TIME_START).total_seconds()))
