# Promiedos Data Scraper

Este proyecto se encarga de guardar los resultados de los partidos del día anterior de la página [PROMIEDOS](https://www.promiedos.com.ar/) en una base de datos PostgreSQL, a partir de la lectura del HTML, con el fin de que persistan los datos ya que estos se borran de la web luego de pasados dos días del partido.

## Estructura del proyecto

```bash
.
├── data_output_example.html
├── main_deprecated.py
├── main.py
├── README.md
├── requirements.txt
├── sql
│   └── create_table.sql
└── template.env

```

## Instalación de dependencias

Se debe usar el gestor de dependencias [pip](https://pip.pypa.io/en/stable/):

```bash
pip install -r requirements.txt
```

Luego para configurar un ambiente propio se debe reemplazar los datos propios en el archivo template.env:

## Uso

Al ejecutar el archivo main.py comienza el proceso ETL para concluir con el guardado de datos

```Uso
python3 main.py
```

## Visualización de datos

El proyecto actualmente se encuentra en producción y pueden verse los datos almacenados en [Grafana](https://promiedos-dashboard.herokuapp.com/d/OWjDW3unk/dashboard-promiedos?orgId=1)
