#!/usr/bin/env python

import logging
import re
from datetime import date, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup
from decouple import config
from sqlalchemy import create_engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    level=logging.INFO,
    filemode="a"
    )
logger = logging.getLogger(__name__)

today = date.today()
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime("%d-%m-%Y")

user = config('POSTGRES_USER')
passwd = config('POSTGRES_PASSWORD')
host = config('POSTGRES_HOST')
port = config('POSTGRES_PORT')
db = config('POSTGRES_DATABASE')
dbschema = config('POSTGRES_SCHEMA')
url = f'postgresql://{user}:{passwd}@{host}:{port}/{db}'

eng = create_engine(
    url,
    connect_args={
        'options': '-csearch_path={}'.format(dbschema)},
    isolation_level="AUTOCOMMIT")


def extract():
    page = requests.get('https://www.promiedos.com.ar/ayer')
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all(id="fixturein")
    return tables


def transform(tables):
    fecha_partido = yesterday
    df_columnas = ['equipo_local',
                   'equipo_visitante',
                   'goles_local',
                   'goles_visitante',
                   'torneo',
                   'goleadores_local',
                   'goleadores_visitante',
                   'detalle',
                   'fecha_partido']

    df_partidos = pd.DataFrame(columns=df_columnas)

    for table in tables:
        torneo = table.find('tr', class_="tituloin").text.strip(' ')
        partidos = table.find_all('tr', id=re.compile('^\\d{1,3}_?\\d+$'))
        try:
            detalle = table.find('tr', class_="choy").text.strip(' ')
        except Exception as e:
            detalle = ''
        for partido in partidos:
            partido_id = partido.get('id')
            equipo_local = partido.find(
                'span', id=re.compile('^t1[\\d_]*$')).text.strip(' ')
            goles_local = partido.find('td', class_="game-r1").text.strip(' ')
            goles_visitante = partido.find(
                'td', class_="game-r2").text.strip(' ')
            equipo_visitante = partido.find(
                'span', id=re.compile('^t2[\\d_]*$')).text.strip(' ')
            try:
                goleadores_local = table.find(
                    'td', id="g1_" + partido_id).text.strip(' ')
            except Exception as e:
                goleadores_local = ''
            try:
                goleadores_visitante = table.find(
                    'td', id="g2_" + partido_id).text.strip(' ')
            except Exception as e:
                goleadores_visitante = ''

            df_partido = pd.DataFrame([[equipo_local,
                                        equipo_visitante,
                                        goles_local,
                                        goles_visitante,
                                        torneo,
                                        goleadores_local,
                                        goleadores_visitante,
                                        detalle,
                                        fecha_partido]], columns=df_columnas)

            df_partidos = pd.concat([df_partidos, df_partido])
    return df_partidos


def load(df):
    with eng.connect() as conn:
        df.to_sql(
            'partidos',
            schema=dbschema,
            con=conn,
            index=False,
            if_exists='append')


def main():
    data = extract()
    data_transformed = transform(data)
    load(data_transformed)


if __name__ == '__main__':
    try:
        main()
        logger.info('Se han ejecutado el proceso ETL exitosamente')
    except Exception as e:
        logger.error(f'Ha fallado al menos una tarea en el proceso: {e}')

