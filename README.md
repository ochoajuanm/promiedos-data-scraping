# Promiedos Data Scraper

Este proyecto se encarga de guardar los resultados de los partidos del día anterior de la página [PROMIEDOS](https://www.promiedos.com.ar/) en una base de datos PostgreSQL, a partir de la lectura del HTML, con el fin de que persistan los datos ya que estos se borran de la web luego de pasados dos días del partido.

## Estructura del proyecto

```bash
.
├── crontab.Development
├── data_output_example.html
├── Dockerfile
├── jobs
│   └── main.py
├── README.md
├── requirements.txt
├── sql
│   ├── create_table.sql
│   └── delete_duplicates.sql
├── start.sh
└── template.env

```

## Instalación de dependencias

Se debe usar el gestor de dependencias [pip](https://pip.pypa.io/en/stable/):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Luego para configurar un ambiente propio se debe reemplazar los datos propios en el archivo template.env:

## Uso

Al ejecutar el archivo main.py comienza el proceso ETL para concluir con el guardado de datos

```Uso
python3 jobs/main.py
```

## Visualización de datos

El proyecto actualmente se encuentra en producción y pueden verse los datos almacenados en [Grafana](https://promiedos-dashboard.herokuapp.com/d/OWjDW3unk/dashboard-promiedos?orgId=1)


