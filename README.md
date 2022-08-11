[![Promiedos](https://www.promiedos.com.ar/images/menu/logo2.jpg)](https://www.promiedos.com.ar/)

# Promiedos Data Scraper

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-%230D597F.svg?style=for-the-badge&logo=alpine-linux&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)


Este proyecto se encarga de realizar scraping con la librería `bs4` (Beautiful Soup) de Python, leyendo HTML mediante RegEx; transformar los datos con `pandas` y guardar los resultados de los partidos del día anterior de la página [PROMIEDOS](https://www.promiedos.com.ar/) en una base de datos PostgreSQL en la nube, con el fin de que persistan los registros de los partidos de futbol diarios ya que estos se borran de la web luego de pasados dos días del partido.

## Estructura del proyecto

```bash
.
├── crontab.Development # Schedule de proceso ETL a ejecutarse (jobs/main.py)
├── data_output_example.html # Un ejemplo de los datos que scrapeamos
├── Dockerfile 
├── jobs
│   └── main.py
├── README.md
├── requirements.txt
├── sql
│   ├── create_table.sql # Crear la tabla en caso de no existir
│   └── delete_duplicates.sql
├── start.sh # Definimos entrypoint para desplegar la aplicación
└── template.env

```

## Instalación de dependencias

Se debe usar el gestor de dependencias [pip](https://pip.pypa.io/en/stable/):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Luego para configurar un ambiente persional se deben reemplazar los datos propios en el archivo `template.env` y renombrarlo como `.env`. Gracias a la librería `decouple` se leerán las variables de entorno

## Uso

Al ejecutar el archivo main.py comienza el proceso ETL para concluir con el guardado de datos

```bash
python3 jobs/main.py
```

## Deploy

El `Dockerfile` nos sirve para desplegar nuestra aplicación, está configurado de tal forma de partir de una imagen de Alpine personalizada (ya que la imagen original de Alpine presenta conflictos con `pandas`), y usando el archivo `start.sh` creará el schedule solicitado en `crontab.Development` para que se ejecute automáticamente todos los días. Para realizar deploy de esta forma:

```bash
docker build -t scheduler .
docker run -it scheduler /bin/bash
source start.sh
```

## Visualización de datos

El proyecto actualmente se encuentra en producción y pueden verse los datos almacenados en [Grafana](https://promiedos-dashboard.herokuapp.com/d/OWjDW3unk/dashboard-promiedos?orgId=1)


