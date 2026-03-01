import datetime

# UoL 2025/26 term blocks: (first_week_num, monday_date, num_weeks, label)
TERM_BLOCKS = {
    1: [
        (1, datetime.date(2025, 9, 22), 12, 'Teaching'),
    ],
    2: [
        (1, datetime.date(2026, 1, 26), 8, 'Teaching'),
        (9, datetime.date(2026, 4, 13), 4, 'Teaching'),
    ],
}


def get_current_semester():
    """Determine which semester we're in based on today's date."""
    today = datetime.date.today()
    sem2_start = TERM_BLOCKS[2][0][1]
    sem1_start = TERM_BLOCKS[1][0][1]
    if today >= sem2_start:
        return 2
    if today >= sem1_start:
        return 1
    return 1  # default fallback


def get_week_monday(semester, week_num):
    """Return the Monday date for a given semester week number."""
    for block_start, block_monday, num_weeks, _ in TERM_BLOCKS[semester]:
        block_end = block_start + num_weeks - 1
        if block_start <= week_num <= block_end:
            return block_monday + datetime.timedelta(weeks=week_num - block_start)
    return None


def get_current_week(semester):
    """Return the current week number for the semester, or 1 if outside term."""
    today = datetime.date.today()
    for block_start, block_monday, num_weeks, _ in TERM_BLOCKS[semester]:
        block_end_date = block_monday + datetime.timedelta(weeks=num_weeks)
        if block_monday <= today < block_end_date:
            return block_start + (today - block_monday).days // 7
    return 1


def get_term_info(semester, week_num):
    """Return term period info for the banner display."""
    for block_start, block_monday, num_weeks, label in TERM_BLOCKS[semester]:
        block_end = block_start + num_weeks - 1
        if block_start <= week_num <= block_end:
            end_friday = block_monday + datetime.timedelta(weeks=num_weeks - 1, days=4)
            return {
                'label': label,
                'start': block_monday,
                'end': end_friday,
                'total_weeks': num_weeks,
                'week_in_block': week_num - block_start + 1,
            }
    return None


def get_max_week(semester):
    """Return the maximum week number for a semester."""
    last = TERM_BLOCKS[semester][-1]
    return last[0] + last[2] - 1


def parse_weeks(weeks_str):
    """Parse weeks string like '1-8,9-12' into a set of week numbers."""
    if not weeks_str:
        return set()
    result = set()
    for part in weeks_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(part))
    return result
