import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

SOURCE_URL = "http://raspisanie.nikasoft.ru/12210248.html"
OUTPUT_FILE = "schedule.json"
TIMEOUT = 20
MAX_SIZE = 5 * 1024 * 1024


def empty_schedule():
    return {
        "updatedAt": None,
        "sourceStatus": "unavailable",
        "classes": {}
    }


def fetch_source():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "ScheduleSync/1.0",
            "Accept": "text/html"
        }
    )

    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status")

        content_type = response.headers.get("Content-Type", "").lower()

        if "html" not in content_type:
            raise ValueError("Source is not HTML")

        data = response.read(MAX_SIZE + 1)

        if len(data) > MAX_SIZE:
            raise ValueError("Response is too large")

        charset = response.headers.get_content_charset() or "utf-8"
        html = data.decode(charset, errors="replace")

    if not html.strip():
        raise ValueError("Empty response")

    lowered = html.lower()

    error_markers = [
        "504 gateway time-out",
        "502 bad gateway",
        "503 service unavailable",
        "404 not found",
        "access denied"
    ]

    if any(marker in lowered for marker in error_markers):
        raise ValueError("Source returned an error page")

    if "<html" not in lowered and "<!doctype html" not in lowered:
        raise ValueError("Invalid HTML")

    return html


def main():
    result = empty_schedule()

    try:
        html = fetch_source()

        result["sourceStatus"] = "available"
        result["updatedAt"] = datetime.now(
            timezone.utc
        ).isoformat()

        print("Источник доступен.")
        print("Размер страницы:", len(html), "символов")
        print("Уроки пока не извлечены.")

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError
    ) as error:
        print("Расписание недоступно:", error)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print("Результат сохранён:", result["sourceStatus"])


if __name__ == "__main__":
    main()
