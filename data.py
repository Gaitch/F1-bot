import fastf1
import pandas as pd
from datetime import datetime


def get_driver_standings():
    current_year = datetime.now().year    
    ergast = fastf1.ergast.Ergast()

    response = ergast.get_driver_standings(
    season=current_year,
    result_type="pandas"
    )

    df = response.content[0]
    df = df[[
        "position",
        "driverCode",
        "points",
        "wins"
    ]]

    lines = []

    # Header
    lines.append(f"{'POS':<5} {'DRV':<5} {'PTS':>5} {'WINS':>5}")
    lines.append("-" * 28)

    for _, row in df.iterrows():
        name = str(row["driverCode"])
        position = str(row["position"])
        points = str(int(row["points"]))
        wins = str(row["wins"])

        lines.append(
            f"{position:<5} {name:<5} {points:>5} {wins:>5}"
        )

    text = "\n".join(lines)
    text = f"```\n{text}\n```"
    return text


def get_next_event():
    today = pd.Timestamp.now(tz="Europe/Zurich").tz_localize(None)
    schedule = fastf1.get_events_remaining(dt=today)
    nextevent = schedule.head(1)


    s = nextevent.iloc[0]

    output = f"**Next Event: {s['EventName']}**\n"
    output += f"Location: {s['Location']}\n\n"
    output += "**Schedule**\n"
    output += "```"

    for i in range(1, 6):
        session = s.get(f"Session{i}")
        date = s.get(f"Session{i}Date")

        if session and pd.notna(date):
            output += f"\n{session:<20} {date.strftime('%a, %d %b — %H:%M')}"

    output += "\n```"

    return output


def get_last_race_results():
    current_year = datetime.now().year    
    schedule = fastf1.get_event_schedule(current_year)
    today = pd.Timestamp.now().normalize()

    # Find races that have already taken place
    past_races = schedule[
        (schedule["EventDate"] < today) &
        (schedule["RoundNumber"] > 0)
    ]

    if past_races.empty:
        output = "No completed races found."
    else:
        last_race = past_races.iloc[-1]

        session = fastf1.get_session(
            int(last_race["EventDate"].year),
            last_race["EventName"],
            "R"
        )

        session.load(
            laps=False,
            telemetry=False,
            weather=False,
            messages=False
            )
        results = session.results

        output = f"**Results: {last_race['EventName']}**\n"
        output += "```\n"
        output += f"{'POS':<5}{'DRIVER':<8}{'TEAM':<18}{'PTS':>3}\n"
        output += "-" * 40 + "\n"

        for _, row in results.head(22).iterrows():
            pos = row["Position"]
            position = int(pos) if pd.notna(pos) else "-"

            driver = row["Abbreviation"]
            team = row["TeamName"]
            points = row["Points"]

            points = int(points) if pd.notna(points) else 0

            output += (
                f"{position:<5}"
                f"{driver:<8}"
                f"{team[:21]:<18}"
                f"{points:>3}\n"
            )
        output += "```"
    return output


def get_upcoming_session():
    today = pd.Timestamp.now(tz="UTC").tz_localize(None)

    nextevents = fastf1.get_events_remaining(dt=today)

    upcoming_sessions = []

    for _, event in nextevents.iterrows():

        for i in range(1, 6):
            session_name = event[f"Session{i}"]
            raw_date = event[f"Session{i}DateUtc"]

            if pd.isna(raw_date) or pd.isna(session_name):
                continue

            session_date = pd.Timestamp(raw_date)
            delta_time = (session_date - today).total_seconds()

            if delta_time > 0:
                upcoming_sessions.append(
                    (session_name, session_date, delta_time, event["EventName"])
                )

    upcoming_sessions.sort(key=lambda x: x[1])
    return upcoming_sessions[0]