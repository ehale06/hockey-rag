import json
from pathlib import Path
from datetime import datetime

KEY_PLAYERS = {
    "New Jersey Devils": ["Jack Hughes", "Nico Hischier", "Jesper Bratt"],
    "Carolina Hurricanes": ["Sebastian Aho", "Andrei Svechnikov", "Seth Jarvis"],
    "New York Islanders": ["Mathew Barzal", "Bo Horvat", "Brock Nelson"]
}

OLYMPIC_BREAK_DATE = "2026-02-25"

def load_json(filename: str):
    path = Path("data") / filename
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)

def process_news(articles: list) -> list:
    documents = []
    for article in articles:
        text = f"Title: {article['title']}\n"
        if article.get('published'):
            text += f"Published: {article['published']}\n"
        text += f"Summary: {article['summary']}"
        documents.append({
            "text": text,
            "source": article.get("source", "news"),
            "type": "news"
        })
    return documents

def process_standings(data: dict) -> list:
    documents = []
    for team in data.get("standings", []):
        name = team.get("teamName", {}).get("default", "")
        abbrev = team.get("teamAbbrev", {}).get("default", "")
        points = team.get("points", 0)
        wins = team.get("wins", 0)
        losses = team.get("losses", 0)
        ot_losses = team.get("otLosses", 0)
        games_played = team.get("gamesPlayed", 0)
        division = team.get("divisionName", "")
        conference = team.get("conferenceName", "")
        division_rank = team.get("divisionSequence", "")
        conference_rank = team.get("conferenceSequence", "")

        text = (
            f"Team: {name} ({abbrev})\n"
            f"Division: {division} | Conference: {conference}\n"
            f"Record: {wins}-{losses}-{ot_losses} | "
            f"Games Played: {games_played} | Points: {points}\n"
            f"Division Rank: {division_rank} | Conference Rank: {conference_rank}"
        )
        documents.append({
            "text": text,
            "source": "standings",
            "type": "standings",
            "team": name
        })
    return documents

def process_roster(data: dict, team_name: str) -> list:
    documents = []
    for position_group in ["forwards", "defensemen", "goalies"]:
        for player in data.get(position_group, []):
            first = player.get("firstName", {}).get("default", "")
            last = player.get("lastName", {}).get("default", "")
            number = player.get("sweaterNumber", "")
            position = player.get("positionCode", "")
            shoots = player.get("shootsCatches", "")

            text = (
                f"Player: {first} {last} | Team: {team_name}\n"
                f"Position: {position} | Number: #{number} | "
                f"Shoots/Catches: {shoots}"
            )
            documents.append({
                "text": text,
                "source": "roster",
                "type": "roster",
                "team": team_name,
                "player": f"{first} {last}"
            })
    return documents

def process_team_stats(data: dict, team_name: str) -> list:
    documents = []
    for position_group in ["skaters", "goalies"]:
        for player in data.get(position_group, []):
            first = player.get("firstName", {}).get("default", "")
            last = player.get("lastName", {}).get("default", "")
            position = player.get("positionCode", "")
            games = player.get("gamesPlayed", 0)

            if position_group == "skaters":
                goals = player.get("goals", 0)
                assists = player.get("assists", 0)
                points = player.get("points", 0)
                plus_minus = player.get("plusMinus", 0)
                pim = player.get("penaltyMinutes", 0)
                shots = player.get("shots", 0)

                text = (
                    f"Player: {first} {last} | Team: {team_name} | Position: {position}\n"
                    f"Games Played: {games} | Goals: {goals} | Assists: {assists} | "
                    f"Points: {points} | +/-: {plus_minus}\n"
                    f"PIM: {pim} | Shots: {shots}"
                )
            else:
                wins = player.get("wins", 0)
                losses = player.get("losses", 0)
                ot = player.get("otLosses", 0)
                gaa = player.get("goalsAgainstAverage", 0)
                sv_pct = player.get("savePctg", 0)
                shutouts = player.get("shutouts", 0)

                text = (
                    f"Player: {first} {last} | Team: {team_name} | Position: Goalie\n"
                    f"Games Played: {games} | Record: {wins}-{losses}-{ot}\n"
                    f"GAA: {gaa:.2f} | SV%: {sv_pct:.3f} | Shutouts: {shutouts}"
                )

            documents.append({
                "text": text,
                "source": "stats",
                "type": "player_stats",
                "team": team_name,
                "player": f"{first} {last}"
            })
    return documents

def process_team_scoring_summary(data: dict, team_name: str) -> list:
    skaters = []
    for player in data.get("skaters", []):
        first = player.get("firstName", {}).get("default", "")
        last = player.get("lastName", {}).get("default", "")
        goals = player.get("goals", 0)
        assists = player.get("assists", 0)
        points = player.get("points", 0)
        games = player.get("gamesPlayed", 0)
        position = player.get("positionCode", "")
        skaters.append({
            "name": f"{first} {last}",
            "position": position,
            "games": games,
            "goals": goals,
            "assists": assists,
            "points": points
        })

    skaters_sorted = sorted(skaters, key=lambda x: x["points"], reverse=True)

    lines = [f"Top scorers for {team_name} ranked by points this season:"]
    for i, player in enumerate(skaters_sorted[:10], 1):
        lines.append(
            f"{i}. {player['name']} ({player['position']}) — "
            f"{player['points']} points ({player['goals']}G, {player['assists']}A) "
            f"in {player['games']} games"
        )

    text = "\n".join(lines)
    return [{
        "text": text,
        "source": "stats",
        "type": "scoring_summary",
        "team": team_name,
        "player": ""
    }]

def process_player_game_log(games: list, player_name: str, team_name: str) -> list:
    if not games:
        return []

    documents = []
    games_sorted = sorted(games, key=lambda x: x.get("gameDate", ""))

    # Full season summary
    total_goals = sum(g.get("goals", 0) for g in games_sorted)
    total_assists = sum(g.get("assists", 0) for g in games_sorted)
    total_points = sum(g.get("points", 0) for g in games_sorted)
    total_games = len(games_sorted)
    gwg = sum(g.get("gameWinningGoals", 0) for g in games_sorted)
    total_shots = sum(g.get("shots", 0) for g in games_sorted)

    season_text = (
        f"Season summary for {player_name} ({team_name}) 2025-26:\n"
        f"Games Played: {total_games} | Goals: {total_goals} | "
        f"Assists: {total_assists} | Points: {total_points}\n"
        f"Game Winning Goals: {gwg} | Total Shots: {total_shots}\n"
        f"Points per game: {total_points/total_games:.2f}"
    )
    documents.append({
        "text": season_text,
        "source": "game_log",
        "type": "season_summary",
        "team": team_name,
        "player": player_name
    })

    # Post Olympic break summary
    post_olympic = [
        g for g in games_sorted
        if g.get("gameDate", "") >= OLYMPIC_BREAK_DATE
    ]

    if post_olympic:
        po_goals = sum(g.get("goals", 0) for g in post_olympic)
        po_assists = sum(g.get("assists", 0) for g in post_olympic)
        po_points = sum(g.get("points", 0) for g in post_olympic)
        po_games = len(post_olympic)
        po_gwg = sum(g.get("gameWinningGoals", 0) for g in post_olympic)
        po_shots = sum(g.get("shots", 0) for g in post_olympic)

        post_olympic_text = (
            f"Post Olympic break performance for {player_name} ({team_name}) "
            f"since {OLYMPIC_BREAK_DATE}:\n"
            f"Games Played: {po_games} | Goals: {po_goals} | "
            f"Assists: {po_assists} | Points: {po_points}\n"
            f"Game Winning Goals: {po_gwg} | Shots: {po_shots}\n"
            f"Points per game since Olympic break: {po_points/po_games:.2f}"
        )
        documents.append({
            "text": post_olympic_text,
            "source": "game_log",
            "type": "post_olympic_summary",
            "team": team_name,
            "player": player_name
        })

    # Last 10 games summary
    last_10 = games_sorted[-10:]
    l10_goals = sum(g.get("goals", 0) for g in last_10)
    l10_assists = sum(g.get("assists", 0) for g in last_10)
    l10_points = sum(g.get("points", 0) for g in last_10)
    l10_gwg = sum(g.get("gameWinningGoals", 0) for g in last_10)

    last_10_text = (
        f"Last 10 games for {player_name} ({team_name}):\n"
        f"Goals: {l10_goals} | Assists: {l10_assists} | Points: {l10_points}\n"
        f"Game Winning Goals: {l10_gwg}\n"
        f"Points per game last 10: {l10_points/10:.2f}\n"
        f"Game by game: " +
        ", ".join([
            f"{g.get('gameDate','')}: {g.get('goals',0)}G {g.get('assists',0)}A vs {g.get('opponentCommonName',{}).get('default','')}"
            for g in last_10
        ])
    )
    documents.append({
        "text": last_10_text,
        "source": "game_log",
        "type": "last_10_games",
        "team": team_name,
        "player": player_name
    })

    # Individual game documents
    for game in games_sorted:
        date = game.get("gameDate", "")
        opponent = game.get("opponentCommonName", {}).get("default", "")
        home_road = "home" if game.get("homeRoadFlag") == "H" else "away"
        goals = game.get("goals", 0)
        assists = game.get("assists", 0)
        points = game.get("points", 0)
        plus_minus = game.get("plusMinus", 0)
        shots = game.get("shots", 0)
        toi = game.get("toi", "")
        gwg = game.get("gameWinningGoals", 0)
        ppp = game.get("powerPlayPoints", 0)

        game_text = (
            f"{player_name} game log entry — {date} vs {opponent} ({home_road}):\n"
            f"Goals: {goals} | Assists: {assists} | Points: {points} | "
            f"+/-: {plus_minus}\n"
            f"Shots: {shots} | TOI: {toi} | PP Points: {ppp}"
        )
        if gwg:
            game_text += f" | GAME WINNING GOAL"

        documents.append({
            "text": game_text,
            "source": "game_log",
            "type": "single_game",
            "team": team_name,
            "player": player_name,
            "date": date
        })

    return documents

if __name__ == "__main__":
    TEAMS = {
        "NJD": "New Jersey Devils",
        "CAR": "Carolina Hurricanes",
        "NYI": "New York Islanders"
    }

    all_documents = []

    print("Processing news articles...")
    news = load_json("news_all.json")
    news_docs = process_news(news)
    all_documents.extend(news_docs)
    print(f"Created {len(news_docs)} news documents")

    print("Processing standings...")
    standings = load_json("standings.json")
    standings_docs = process_standings(standings)
    all_documents.extend(standings_docs)
    print(f"Created {len(standings_docs)} standings documents")

    for abbrev, name in TEAMS.items():
        print(f"Processing {name}...")

        roster = load_json(f"roster_{abbrev}.json")
        roster_docs = process_roster(roster, name)
        all_documents.extend(roster_docs)

        stats = load_json(f"stats_{abbrev}.json")
        stats_docs = process_team_stats(stats, name)
        all_documents.extend(stats_docs)

        scoring_summary = process_team_scoring_summary(stats, name)
        all_documents.extend(scoring_summary)
        print(f"Added scoring summary for {name}")

    print("\nProcessing player game logs...")
    all_key_players = []
    for team_name, players in KEY_PLAYERS.items():
        for player_name in players:
            all_key_players.append((player_name, team_name))

    for player_name, team_name in all_key_players:
        safe_name = player_name.replace(" ", "_")
        games = load_json(f"gamelog_{safe_name}.json")
        if games:
            game_docs = process_player_game_log(games, player_name, team_name)
            all_documents.extend(game_docs)
            print(f"Processed {len(game_docs)} documents for {player_name}")
        else:
            print(f"No game log found for {player_name}")

    print(f"\nTotal documents created: {len(all_documents)}")

    with open(Path("data") / "processed_documents.json", "w") as f:
        json.dump(all_documents, f, indent=2)
    print("Saved processed_documents.json")