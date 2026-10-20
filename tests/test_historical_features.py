import copy
import unittest
from ufc_predictor.processing.build_historical_features import build_historical_features


def record(identifier, day, a='A', b='B', result='W', landed=10, attempted=20):
    def fighter(fid, outcome):
        return {'fighter_id': fid, 'weight_lbs': 999,
                'fight_stats': {'fighter_id': fid, 'result': outcome,
                                'sig_str_landed': landed, 'sig_str_attempted': attempted,
                                'td_landed': 0, 'td_attempted': 0}}
    return {'fight': {'fight_id': identifier, 'event_id': 'event-' + str(day),
                      'event_year': 2023, 'event_month': 1, 'event_day': day},
            'fighter_a': fighter(a, result),
            'fighter_b': fighter(b, {'W': 'L', 'L': 'W', 'D': 'D', 'NC': 'NC'}[result])}


class HistoricalFeatureTests(unittest.TestCase):
    def test_first_observation_is_unknown(self):
        row = build_historical_features([record('1', 1)])[0]
        self.assertEqual(row['features']['fighter_a']['prior_fights'], 0)
        self.assertIsNone(row['features']['fighter_a']['sig_str_accuracy'])
        self.assertIsNone(row['features']['fighter_a']['avg_ctrl_seconds'])
        self.assertNotIn('weight_lbs', row['features']['fighter_a'])

    def test_current_and_future_mutation_cannot_change_features(self):
        records = [record('1', 1), record('2', 2), record('3', 3)]
        before = build_historical_features(records)
        changed = copy.deepcopy(records)
        changed[1] = record('2', 2, result='L', landed=500, attempted=500)
        changed[2] = record('3', 3, result='L', landed=999, attempted=999)
        after = build_historical_features(changed)
        self.assertEqual(before[0], after[0])
        self.assertEqual(before[1]['features'], after[1]['features'])
        self.assertNotEqual(before[1]['labels'], after[1]['labels'])
        self.assertEqual(before[:2], build_historical_features(records[:2]))

    def test_same_day_excluded_and_input_order_irrelevant(self):
        records = [record('2', 1, b='C'), record('1', 1), record('3', 2)]
        rows = build_historical_features(records)
        self.assertEqual(rows, build_historical_features(reversed(records)))
        self.assertEqual([r['features']['fighter_a']['prior_fights'] for r in rows], [0, 0, 2])

    def test_identity_follows_fighter_across_sides(self):
        rows = build_historical_features([record('1', 1), record('2', 3, a='C', b='A')])
        features = rows[1]['features']['fighter_b']
        self.assertEqual(features['prior_wins'], 1)
        self.assertEqual(features['days_since_last_fight'], 2)
        self.assertEqual(features['sig_str_accuracy'], 0.5)

    def test_weighted_accuracy_and_missing_values(self):
        rows = build_historical_features([record('1', 1, landed=1, attempted=2),
                                          record('2', 2, landed=9, attempted=10), record('3', 3)])
        features = rows[2]['features']['fighter_a']
        self.assertAlmostEqual(features['sig_str_accuracy'], 10 / 12)
        self.assertAlmostEqual(features['sig_str_defense'], 1 - 10 / 12)
        self.assertIsNone(features['td_accuracy'])
        self.assertIsNone(features['avg_ctrl_seconds'])
        self.assertEqual(features['ctrl_seconds_observed_fights'], 0)

    def test_draw_and_nc_not_binary_losses(self):
        rows = build_historical_features([record('1', 1, result='D'),
                                          record('2', 2, result='NC'), record('3', 3)])
        self.assertIsNone(rows[0]['labels']['fighter_a_win'])
        self.assertIsNone(rows[1]['labels']['fighter_a_win'])
        self.assertEqual(rows[2]['features']['fighter_a']['prior_draws'], 1)
        self.assertEqual(rows[2]['features']['fighter_a']['prior_no_contests'], 1)
        self.assertIsNone(rows[2]['features']['fighter_a']['win_rate_decisive'])

    def test_duplicate_invalid_date_and_mismatched_identity_rejected(self):
        original = record('1', 1)
        with self.assertRaises(ValueError):
            build_historical_features([original, original])
        with self.assertRaises(ValueError):
            build_historical_features([record('1', 32)])
        original['fighter_a']['fight_stats']['fighter_id'] = 'wrong'
        with self.assertRaises(ValueError):
            build_historical_features([original])


if __name__ == '__main__':
    unittest.main()