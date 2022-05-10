CREATE TABLE IF NOT EXISTS myschema.partidos(
        equipo_local CHARACTER VARYING,
        equipo_visitante CHARACTER VARYING,
        goles_local INTEGER,
        goles_visitante INTEGER,
        torneo CHARACTER VARYING,
        goleadores_local CHARACTER VARYING,
        goleadores_visitante CHARACTER VARYING,
        estado_partido CHARACTER VARYING,
        detalle CHARACTER VARYING,
        fecha_partido CHARACTER VARYING,
    )
