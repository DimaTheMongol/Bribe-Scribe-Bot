import sqlite3
from datetime import datetime, timezone
from typing import Optional

import re
from typing import Iterable, List, Tuple, Optional

DB_PATH = "bribe_scribe.db"
# Accept common separators: "vs", "v", "-", "—"
_FIXTURE_RE = re.compile(
    r"^\s*(?P<home>.+?)\s*(?:vs\.?|v\.?|-\s*|—\s*)\s*(?P<away>.+?)\s*$",
    re.IGNORECASE,
)

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_betting_db() -> None:
    """Create betting tables if they do not exist yet."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fixtures (
                fixture_id INTEGER PRIMARY KEY AUTOINCREMENT,
                season TEXT NOT NULL,
                round INTEGER NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'scheduled',  -- scheduled|locked|completed|void
                home_score INTEGER,
                away_score INTEGER,
                result TEXT,                                -- home|draw|away|void
                created_at TEXT NOT NULL,
                locked_at TEXT,
                completed_at TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS markets (
                market_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER NOT NULL,
                market_type TEXT NOT NULL,                  -- moneyline_1x2
                odds_home REAL NOT NULL,
                odds_draw REAL NOT NULL,
                odds_away REAL NOT NULL,
                margin REAL NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (fixture_id) REFERENCES fixtures (fixture_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bets (
                bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fixture_id INTEGER NOT NULL,
                market_id INTEGER NOT NULL,
                selection TEXT NOT NULL,                    -- home|draw|away
                stake INTEGER NOT NULL,
                odds_taken REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',         -- open|won|lost|push|void
                payout INTEGER NOT NULL DEFAULT 0,
                placed_at TEXT NOT NULL,
                settled_at TEXT,
                FOREIGN KEY (fixture_id) REFERENCES fixtures (fixture_id),
                FOREIGN KEY (market_id) REFERENCES markets (market_id)
            )
            """
        )

        conn.commit()

def parse_fixture_lines(text: str) -> List[Tuple[str, str]]:
    """
    Parses a pasted block of fixtures into [(home_team, away_team), ...].

    Expected line formats (examples):
      Shiny Klawz vs The Ball Boys
      Shiny Klawz v The Ball Boys
      Shiny Klawz - The Ball Boys

    Blank lines are ignored.
    """
    fixtures: List[Tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m = _FIXTURE_RE.match(line)
        if not m:
            raise ValueError(
                f"Could not parse fixture line: '{raw_line}'. "
                "Use format like: Team A vs Team B"
            )

        home = m.group("home").strip()
        away = m.group("away").strip()

        if not home or not away:
            raise ValueError(f"Invalid fixture line: '{raw_line}'")

        fixtures.append((home, away))

    if not fixtures:
        raise ValueError("No fixtures found. Paste at least one line like: Team A vs Team B")

    return fixtures

def create_fixtures_for_round(
    season: str,
    round_number: int,
    fixtures: List[Tuple[str, str]],
) -> int:
    """
    Inserts fixtures into the fixtures table.
    Returns the number of fixtures inserted.

    Prevents duplicates for the same season/round/home/away.
    """
    created_at = now_iso()

    with connect() as conn:
        # Optional: prevent duplicate insertion if rerun
        existing = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM fixtures
            WHERE season = ? AND round = ?
            """,
            (season, round_number),
        ).fetchone()

        if int(existing["c"]) > 0:
            raise ValueError(f"Round {round_number} already has fixtures in the DB. Use a different round or clear them first.")

        for home, away in fixtures:
            conn.execute(
                """
                INSERT INTO fixtures (season, round, home_team, away_team, status, created_at)
                VALUES (?, ?, ?, ?, 'scheduled', ?)
                """,
                (season, round_number, home, away, created_at),
            )

        conn.commit()
        return len(fixtures)

def list_fixtures(season: str, round_number: Optional[int] = None):
    """
    Returns fixtures rows. If round_number is None, returns all fixtures for season.
    """
    with connect() as conn:
        if round_number is None:
            rows = conn.execute(
                """
                SELECT fixture_id, round, home_team, away_team, status, home_score, away_score
                FROM fixtures
                WHERE season = ?
                ORDER BY round ASC, fixture_id ASC
                """,
                (season,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT fixture_id, round, home_team, away_team, status, home_score, away_score
                FROM fixtures
                WHERE season = ? AND round = ?
                ORDER BY fixture_id ASC
                """,
                (season, round_number),
            ).fetchall()
        return rows

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()