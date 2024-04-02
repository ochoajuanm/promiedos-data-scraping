from dataclasses import dataclass


@dataclass
class Match:
    home_team: str
    away_team: str
    home_goals: str
    away_goals: str
    tournament: str
    home_scorers: str
    away_scorers: str
    details: str
    match_date: str
