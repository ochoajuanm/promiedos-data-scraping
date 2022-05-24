import logging
from datetime import date, timedelta
from bs4 import BeautifulSoup
import re

import pandas as pd

import requests

from decouple import config
from sqlalchemy import create_engine

logger = logging.getLogger("").getChild(__name__)

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


eng = create_engine(
    url,
    connect_args={
        'options': '-csearch_path={}'.format(dbschema)},
    isolation_level="AUTOCOMMIT")


# def extract():
#     r = requests.get('https://www.promiedos.com.ar/ayer')
#     soup = BeautifulSoup(html_doc, 'html.parser')

if __name__ == '__main__':
    page = requests.get('https://www.promiedos.com.ar/ayer')
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all(id="fixturein")
    ligas = []
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
        partidos = table.find_all('tr', id=re.compile('^\d{1,3}_?\d+$'))
        goles = table.find_all('tr', class_="goles")
        try:
            detalle = table.find('tr', class_="choy").text.strip(' ')
        except Exception as e:
            detalle = ''
        for partido in partidos:
            partido_id = partido.get('id')
            equipo_local = partido.find('span', id=re.compile('^t1[\d_]*$')).text.strip(' ')
            goles_local = partido.find('td', class_="game-r1").text.strip(' ')
            goles_visitante = partido.find('td', class_="game-r2").text.strip(' ')
            equipo_visitante = partido.find('span', id=re.compile('^t2[\d_]*$')).text.strip(' ')
            try:
                goleadores_local = partido.find('td', id="g1_"+partido_id).text.strip(' ')
            except Exception as e:
                goleadores_local = ''
            try:
                goleadores_visitante = partido.find('td', id="g2_"+partido_id).text.strip(' ')
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
    # df_partidos.to_csv('output.csv', sep=';', encoding='utf8', index=False)

    with eng.connect() as conn:
        df_partidos.to_sql(
                        'partidos',
                        schema=dbschema,
                        con=conn,
                        index=False,
                        if_exists='append')
