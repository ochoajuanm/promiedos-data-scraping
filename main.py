import logging
from datetime import date, timedelta

import pandas as pd
from decouple import config
from sqlalchemy import create_engine

logger = logging.getLogger("").getChild(__name__)

leagues = ['COPA DE LA LIGA', 'PREMIER LEAGUE', 'SERIE A', 'LA LIGA']

today = date.today()
yesterday = today - timedelta(days = 1) 
yesterday = yesterday.strftime("%d-%m-%Y")

user = config('POSTGRES_USER')
passwd = config('POSTGRES_PASSWORD')
host = config('POSTGRES_HOST')
port = config('POSTGRES_PORT')
db = config('POSTGRES_DATABASE')
dbschema = config('POSTGRES_SCHEMA')
url = f'postgresql://{user}:{passwd}@{host}:{port}/{db}'

# MAKE THIS IMPORTANT CHANGE TO USE AUTOCOMMIT TRANSACTIONS WITH BIT.IO
eng = create_engine(
    url,
    connect_args={
        'options': '-csearch_path={}'.format(dbschema)},
    isolation_level="AUTOCOMMIT")


def extract_data(league):
    try:
        df = pd.read_html('https://www.promiedos.com.ar/ayer', match=league)
    except UnicodeDecodeError as e:
        return None
    if league == 'LA LIGA':
        df = df[-1]
        if df.iloc[1, 0] != 'LA LIGA':
            return None
    return df[0]


def transform_data(df):
    df_partidos = pd.DataFrame(columns=['equipo_local',
                                        'equipo_visitante',
                                        'goles_local',
                                        'goles_visitante',
                                        'torneo',
                                        'goleadores_local',
                                        'goleadores_visitante',
                                        'estado_partido',
                                        'detalle',
                                        'fecha_partido'])
    torneo = df.iloc[1, 0]
    if df.iloc[2, 0] != 'Final':
        detalle = df.iloc[2, 0]
        arr = 1
    else:
        detalle = ''
        arr = 0

    estado_partido = 'Final'
    indexes_to_drop = []

    for i in range(len(df)):
        if df.iloc[i, 2] == '0' and df.iloc[i, 3] == '0':
            equipo_local = df.iloc[i, 1]
            goles_local = df.iloc[i, 2]
            goles_visitante = df.iloc[i, 3]
            equipo_visitante = df.iloc[i, 4]
            df_partidos = df_partidos.append(
                {
                    'equipo_local': equipo_local,
                    'equipo_visitante': equipo_visitante,
                    'goles_local': goles_local,
                    'goles_visitante': goles_visitante,
                    'torneo': torneo,
                    'goleadores_local': '',
                    'goleadores_visitante': '',
                    'estado_partido': estado_partido,
                    'detalle': detalle,
                    'fecha_partido': yesterday
                },
                ignore_index=True)
            indexes_to_drop = indexes_to_drop.append(i)

    if indexes_to_drop is not None:
        df.drop(index=indexes_to_drop, inplace=True)

    # Fix out of range if len is less or equal to 3
    if len(df) >= 4:
        for i in range(2 + arr, len(df), 2):
            equipo_local = df.iloc[i, 1]
            goles_local = df.iloc[i, 2]
            goles_visitante = df.iloc[i, 3]
            equipo_visitante = df.iloc[i, 4]
            goleadores_local = df.iloc[i + 1, 1]
            goleadores_visitante = df.iloc[i + 1, 4]
            df_partidos = df_partidos.append(
                {
                    'equipo_local': equipo_local,
                    'equipo_visitante': equipo_visitante,
                    'goles_local': goles_local,
                    'goles_visitante': goles_visitante,
                    'torneo': torneo,
                    'goleadores_local': goleadores_local,
                    'goleadores_visitante': goleadores_visitante,
                    'estado_partido': estado_partido,
                    'detalle': detalle,
                    'fecha_partido': yesterday
                },
                ignore_index=True)

    return df_partidos


def load_data(df, eng, dbschema):
    # Work with sqlalchemy as you normally would
    with eng.connect() as conn:
        df.to_sql(
            'partidos',
            schema=dbschema,
            con=conn,
            index=False,
            if_exists='append')


if __name__ == '__main__':
    for league in leagues:
        extract = extract_data(league)
        if extract is None:
            continue
        transform = transform_data(extract)
        load = load_data(transform, eng, dbschema)
