import requests
import json
from pathlib import Path

TEAMS = {
    "NJD": "New Jersey Devils",
    "CAR": "Carolina Hurricanes",
    "NYI": "New York Islanders"
}

RSS_FEEDS = {
    "espn_nhl": "https://www.espn.com/espn/rss/nhl/news",
    "sportsnet": "https://www.sportsnet.ca/feed/"
}

KEY_PLAYERS = {
    "New Jersey Devils": ["Jack Hughes", "Nico Hischier", "Jesper Bratt"],
    "Carolina Hurricanes": ["Sebastian Aho", "Andrei Svechnikov", "Seth Jarvis"],
    "New York Islanders": ["Mathew Barzal", "Bo Horvat", "Brock Nelson"]
}

def fetch_rss_feed(name: str, url: str) -> list:
    import feedparser
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            summary = entry.get("summary", "").strip()
            title = entry.get("title", "").strip()
            if not summary or len(summary) < 50:
                continue
            articles.append({
                "source": name,
                "title": title,
                "summary": summary,
                "published": entry.get("published", ""),
                "link": entry.get("link", "")
            })
        print(f"Fetched {len(articles)} usable articles from {name}")
        return articles
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return []

def fetch_standings() -> dict:
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    return response.json()

def fetch_roster(team_abbrev: str) -> dict:
    url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/current"
    response = requests.get(url)
    return response.json()

def fetch_schedule(team_abbrev: str) -> dict:
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team_abbrev}/now"
    response = requests.get(url)
    return response.json()

def fetch_team_stats(team_abbrev: str) -> dict:
    url = f"https://api-web.nhle.com/v1/club-stats/{team_abbrev}/now"
    response = requests.get(url)
    return response.json()

def fetch_player_game_log(player_id: int, player_name: str) -> list:
    url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/20252026/2"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        games = data.get("gameLog", [])
        print(f"Fetched {len(games)} games for {player_name}")
        return games
    else:
        print(f"Could not fetch game log for {player_name}")
        return []

def get_player_ids_from_roster(roster: dict, team_name: str) -> dict:
    player_ids = {}
    key_names = KEY_PLAYERS.get(team_name, [])
    for position_group in ["forwards", "defensemen", "goalies"]:
        for player in roster.get(position_group, []):
            first = player.get("firstName", {}).get("default", "")
            last = player.get("lastName", {}).get("default", "")
            full_name = f"{first} {last}"
            if full_name in key_names:
                player_ids[full_name] = player.get("id")
    return player_ids

def save_raw_data(data, filename: str):
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    with open(data_path / filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {filename}")

if __name__ == "__main__":
    # Fetch news
    import feedparser
    print("Fetching news articles...")
    all_articles = []
    for name, url in RSS_FEEDS.items():
        articles = fetch_rss_feed(name, url)
        all_articles.extend(articles)
    save_raw_data(all_articles, "news_all.json")
    print(f"Total usable articles: {len(all_articles)}\n")

    # Fetch standings
    print("Fetching standings...")
    standings = fetch_standings()
    save_raw_data(standings, "standings.json")

    # Fetch team data and game logs
    for abbrev, name in TEAMS.items():
        print(f"\nFetching data for {name}...")

        roster = fetch_roster(abbrev)
        save_raw_data(roster, f"roster_{abbrev}.json")

        schedule = fetch_schedule(abbrev)
        save_raw_data(schedule, f"schedule_{abbrev}.json")

        stats = fetch_team_stats(abbrev)
        save_raw_data(stats, f"stats_{abbrev}.json")

        # Get player IDs and fetch game logs
        player_ids = get_player_ids_from_roster(roster, name)
        print(f"Found player IDs: {player_ids}")

        for player_name, player_id in player_ids.items():
            if player_id:
                games = fetch_player_game_log(player_id, player_name)
                safe_name = player_name.replace(" ", "_")
                save_raw_data(games, f"gamelog_{safe_name}.json")

    print("\nAll data ingestion complete.")