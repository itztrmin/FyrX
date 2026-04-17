from datetime import datetime, timedelta, timezone

# Bangladesh timezone (UTC+6)
BD_TZ = timezone(timedelta(hours=6))

def bangladesh_now():
    """Return current datetime in Bangladesh timezone."""
    return datetime.now(BD_TZ)

def smart_footer_time():
    now = bangladesh_now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        day = "Today"
    elif now.date() == yesterday:
        day = "Yesterday"
    else:
        day = now.strftime("%b %d, %Y")

    return f"{day} at {now.strftime('%H:%M')}"