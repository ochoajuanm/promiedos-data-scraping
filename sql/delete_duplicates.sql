WITH cte AS (
    SELECT 
        equipo_local,
        equipo_visitante,
        goles_local,
        goles_visitante,
        torneo,
        goleadores_local,
        goleadores_visitante,
        estado_partido,
        detalle,
        fecha_partido,
        ROW_NUMBER() OVER (
            PARTITION BY 
                equipo_local,
                equipo_visitante,
                goles_local,
                goles_visitante,
                torneo,
                goleadores_local,
                goleadores_visitante,
                estado_partido,
                detalle,
                fecha_partido
        ) row_num
     FROM 
        "ochoajuanm/promiedos-database"."partidos"
)
DELETE FROM cte
WHERE row_num > 1;
