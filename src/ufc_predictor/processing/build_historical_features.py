"""Build pre-fight history from combined records, using strictly earlier dates.

No profile career totals or current-fight statistics enter features. Counts
refer only to supplied records, not the fighter's complete professional career.
"""
import argparse
from collections import defaultdict
from datetime import date
from itertools import groupby
import json
from pathlib import Path


def event_date(record):
    fight = record['fight']
    return date(fight['event_year'], fight['event_month'], fight['event_day'])


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def historical_features(history, cutoff):
    """History entries contain date, own stats and opponent stats."""
    results = [entry[1]['result'] for entry in history]
    wins, losses = results.count('W'), results.count('L')
    features = {
        'prior_fights': len(history),
        'prior_wins': wins,
        'prior_losses': losses,
        'prior_draws': results.count('D'),
        'prior_no_contests': results.count('NC'),
        'win_rate_decisive': ratio(wins, wins + losses),
        'days_since_last_fight': (cutoff - history[-1][0]).days if history else None,
    }
    # Pairwise complete observations: missing numbers are never replaced by zero.
    for prefix, landed, attempted, opponent in (
        ('sig_str_accuracy', 'sig_str_landed', 'sig_str_attempted', False),
        ('td_accuracy', 'td_landed', 'td_attempted', False),
        ('sig_str_defense', 'sig_str_landed', 'sig_str_attempted', True),
        ('td_defense', 'td_landed', 'td_attempted', True),
    ):
        stats = [entry[2 if opponent else 1] for entry in history]
        pairs = [(s.get(landed), s.get(attempted)) for s in stats]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        value = ratio(sum(a for a, _ in pairs), sum(b for _, b in pairs))
        features[prefix] = 1 - value if opponent and value is not None else value
        features[prefix + '_observed_fights'] = len(pairs)
    for field in ('kd', 'sig_str_landed', 'sig_str_attempted', 'td_landed',
                  'sub_att', 'ctrl_seconds'):
        values = [entry[1].get(field) for entry in history]
        values = [value for value in values if value is not None]
        features['avg_' + field] = ratio(sum(values), len(values))
        features[field + '_observed_fights'] = len(values)
    return features


def validate_records(records):
    seen = set()
    for record in records:
        fight_id = record['fight']['fight_id']
        if not fight_id or fight_id in seen:
            raise ValueError(f'Missing or duplicate fight_id: {fight_id!r}')
        seen.add(fight_id)
        event_date(record)  # Invalid or missing dates must not silently enter history.
        a, b = record['fighter_a'], record['fighter_b']
        if not a['fighter_id'] or not b['fighter_id'] or a['fighter_id'] == b['fighter_id']:
            raise ValueError(f'Invalid fighter IDs in {fight_id}')
        results = []
        for fighter in (a, b):
            stats = fighter['fight_stats']
            if stats['fighter_id'] != fighter['fighter_id']:
                raise ValueError(f'Profile/stat identity mismatch in {fight_id}')
            results.append(stats['result'])
            for field, value in stats.items():
                if field in ('fighter_id', 'name', 'result') or value is None:
                    continue
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < float('inf'):
                    raise ValueError(f'Invalid statistic {field} in {fight_id}')
            for prefix in ('sig_str', 'td'):
                landed, attempted = stats.get(prefix + '_landed'), stats.get(prefix + '_attempted')
                if landed is not None and attempted is not None and landed > attempted:
                    raise ValueError(f'Landed exceeds attempted in {fight_id}')
        if tuple(results) not in (('W', 'L'), ('L', 'W'), ('D', 'D'), ('NC', 'NC')):
            raise ValueError(f'Invalid result pair in {fight_id}: {results}')


def build_historical_features(records):
    """Return rows with identifiers, feature allowlist, and separate labels.

    Emit every fight on a date before updating any history from that date.
    This conservatively excludes same-day fights whose order is unknown.
    """
    records = list(records)
    validate_records(records)
    records.sort(key=lambda r: (event_date(r), r['fight']['fight_id']))
    histories = defaultdict(list)
    rows = []
    for fight_date, daily_records in groupby(records, key=event_date):
        daily_records = list(daily_records)
        for record in daily_records:
            fight = record['fight']
            a, b = record['fighter_a'], record['fighter_b']
            a_features = historical_features(histories[a['fighter_id']], fight_date)
            b_features = historical_features(histories[b['fighter_id']], fight_date)
            result = a['fight_stats']['result']
            rows.append({
                'fight_id': fight['fight_id'],
                'event_id': fight['event_id'],
                'event_name': fight.get('event_name'),
                'event_date': fight_date.isoformat(),

                'fighter_a_id': a['fighter_id'],
                'fighter_a_name': a.get('name'),

                'fighter_b_id': b['fighter_id'],
                'fighter_b_name': b.get('name'),

                'features': {
                    'fighter_a': a_features,
                    'fighter_b': b_features,
                    'matchup': {
                        key + '_diff': (
                            a_features[key] - b_features[key]
                            if a_features[key] is not None
                            and b_features[key] is not None
                            else None
                        )
                        for key in a_features
                    },
                },

                'labels': {
                    'fighter_a_win': (
                        1 if result == 'W'
                        else 0 if result == 'L'
                        else None
                    )
                },
            })
        for record in daily_records:
            a, b = record['fighter_a'], record['fighter_b']
            histories[a['fighter_id']].append((fight_date, a['fight_stats'], b['fight_stats']))
            histories[b['fighter_id']].append((fight_date, b['fight_stats'], a['fight_stats']))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=Path('data/processed'))
    parser.add_argument('--output', type=Path, default=Path('data/processed/historical_features.json'))
    args = parser.parse_args()
    paths = sorted(args.input_dir.glob('*_record.json'))
    if not paths:
        parser.error(f'No *_record.json files found in {args.input_dir}')
    records = [json.loads(path.read_text(encoding='utf-8')) for path in paths]
    rows = build_historical_features(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=4, allow_nan=False) + '\n', encoding='utf-8')
    print(f'Saved {len(rows)} pre-fight rows to {args.output}')


if __name__ == '__main__':
    main()