WITH cte AS (
    SELECT 
        home_team,
        away_team,
        home_goals,
        away_goals,
        tournament,
        home_scorers,
        away_scorers,
        match_status,
        details,
        match_date,
        ROW_NUMBER() OVER (
            PARTITION BY 
                home_team,
                away_team,
                home_goals,
                away_goals,
                tournament,
                home_scorers,
                away_scorers,
                match_status,
                details,
                match_date
        ) row_num
     FROM 
        public.matches
)
DELETE FROM cte
WHERE row_num > 1;
