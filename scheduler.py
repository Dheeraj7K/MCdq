"""
scheduler.py — DKB Daily Auto-Scheduler
Runs in background, triggers generate_batch() 7× per day at scheduled times.
Usage: python scheduler.py
       python scheduler.py --run-now    (run cycle for current time immediately)
       python scheduler.py --cycle 3    (run specific cycle immediately)
"""

import sys
import time
import json
import argparse
from datetime import datetime, date
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
SCHEDULE_FILE = BASE_DIR / "data" / "schedule.json"
SCHEDULE_FILE.parent.mkdir(exist_ok=True)

# ── Schedule: 7 cycle times (hour, minute) ───────────────────────────────────
CYCLE_TIMES = [
    (6,  0),   # Cycle 0 — Foundation
    (9,  0),   # Cycle 1 — Proof
    (12, 0),   # Cycle 2 — Vision
    (15, 0),   # Cycle 3 — Connection
    (18, 0),   # Cycle 4 — Progress
    (21, 0),   # Cycle 5 — Question
    (0,  0),   # Cycle 6 — Breakthrough (midnight)
]

def load_schedule_state() -> dict:
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE) as f:
            return json.load(f)
    return {"completed": {}, "last_run": None}

def save_schedule_state(state: dict):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def is_cycle_done(state: dict, cycle: int) -> bool:
    today = date.today().isoformat()
    return state["completed"].get(today, {}).get(str(cycle), False)

def mark_cycle_done(state: dict, cycle: int):
    today = date.today().isoformat()
    if today not in state["completed"]:
        state["completed"][today] = {}
    state["completed"][today][str(cycle)] = True
    state["last_run"] = datetime.now().isoformat()

def get_current_cycle() -> int | None:
    """Return the cycle index that should run right now (within 5-min window)."""
    now = datetime.now()
    for i, (h, m) in enumerate(CYCLE_TIMES):
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        diff = abs((now - target).total_seconds())
        if diff <= 300:   # within 5 minutes of scheduled time
            return i
    return None

def run_cycle(cycle: int):
    """Import engine and run a batch for the given cycle."""
    from engine import generate_batch
    from server import _build_website
    from engine import get_all_posts, load_theory

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ◈ Running Cycle {cycle+1}/7...")
    posts = generate_batch(cycle, 20)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Cycle {cycle+1} complete — {len(posts)} posts")

    # Rebuild website after each cycle
    all_posts = get_all_posts(300)
    theory    = load_theory()
    _build_website(all_posts, theory)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Website rebuilt — {len(all_posts)} total posts")

def print_status():
    state = load_schedule_state()
    today = date.today().isoformat()
    from engine import CYCLE_THEMES
    THEME_NAMES = [t["name"] for t in CYCLE_THEMES]

    print(f"\n◈ DKB Scheduler Status ({today})")
    print(f"{'─'*50}")
    for i, (h, m) in enumerate(CYCLE_TIMES):
        done   = state["completed"].get(today, {}).get(str(i), False)
        status = "✅ done" if done else "⏳ pending"
        time_s = f"{h:02d}:{m:02d}"
        print(f"  Cycle {i+1}/7  {time_s}  [{THEME_NAMES[i]:12s}]  {status}")
    print(f"{'─'*50}")
    last = state.get("last_run", "never")
    print(f"  Last run: {last}\n")


def main():
    parser = argparse.ArgumentParser(description="DKB Connected Thoughts Scheduler")
    parser.add_argument("--run-now",  action="store_true", help="Run the cycle for the current time immediately")
    parser.add_argument("--cycle",    type=int, default=-1, help="Run a specific cycle (0-6) immediately")
    parser.add_argument("--status",   action="store_true", help="Show schedule status and exit")
    parser.add_argument("--all",      action="store_true", help="Run all 7 cycles immediately (full day)")
    args = parser.parse_args()

    if args.status:
        print_status()
        return

    if args.all:
        print("◈ Running all 7 cycles (full day simulation)...")
        for c in range(7):
            run_cycle(c)
        return

    if args.cycle >= 0:
        print(f"◈ Running cycle {args.cycle} immediately...")
        run_cycle(args.cycle)
        return

    if args.run_now:
        c = get_current_cycle()
        if c is not None:
            run_cycle(c)
        else:
            print("No cycle scheduled within the next 5 minutes.")
            print_status()
        return

    # ── Continuous scheduler loop ─────────────────────────────────────────────
    print("◈ DKB Connected Thoughts Scheduler started")
    print(f"  Schedule: {', '.join(f'{h:02d}:{m:02d}' for h,m in CYCLE_TIMES)}")
    print("  Press Ctrl+C to stop\n")
    print_status()

    while True:
        state = load_schedule_state()
        now   = datetime.now()

        for i, (h, m) in enumerate(CYCLE_TIMES):
            if is_cycle_done(state, i):
                continue
            target_h = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if now >= target_h:
                run_cycle(i)
                mark_cycle_done(state, i)
                save_schedule_state(state)
                break

        # Print heartbeat every hour
        if now.minute == 0 and now.second < 30:
            print(f"[{now.strftime('%H:%M')}] ◈ Scheduler heartbeat — {date.today().isoformat()}")
            print_status()

        time.sleep(30)   # Check every 30 seconds


if __name__ == "__main__":
    main()
