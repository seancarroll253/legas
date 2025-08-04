import json
from datetime import datetime

JOURNAL_FILE = "tagebuch.json"

def migrate_dates():
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    changed = False
    for entry in entries:
        dt_str = entry["datetime"]
        try:
            # Try to parse as ISO — if success, no need to change
            datetime.fromisoformat(dt_str)
        except ValueError:
            # If fails, assume old format and convert
            dt_obj = datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
            entry["datetime"] = dt_obj.isoformat(timespec="seconds")
            changed = True

    if changed:
        with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"Migrated {len(entries)} entries to ISO datetime format.")
    else:
        print("No migration needed, all dates are already in ISO format.")

if __name__ == "__main__":
    migrate_dates()
