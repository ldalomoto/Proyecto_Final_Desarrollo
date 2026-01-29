from datetime import datetime, timedelta, timezone

def should_greet_user(meta: dict) -> bool:
    if meta.get("message_count", 0) <= 1:
        return True

    last_seen = meta.get("last_seen_at")
    if not last_seen:
        return True

    last_seen_dt = datetime.fromisoformat(last_seen)
    now_dt = datetime.now(timezone.utc)

    if now_dt - last_seen_dt > timedelta(minutes=30):
        return True

    return False

