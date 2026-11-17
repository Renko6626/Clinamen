"""Run the production trainer with separate modern diagnostic evaluation.

The config's eval_splits still defines training holdouts. --diagnostic-splits
only changes evaluation, leaving those diagnostic cards in the training pool.
The primary evaluation and best.pt selection use the modern suite; the original
TH06 result is retained separately in every evaluation JSON.
"""
from __future__ import annotations

import argparse
import copy
import json
import time

from stgtrain import console
from stgtrain.cards import configured_cards, load_splits
from stgtrain.evaluate import summarize_eval
import stgtrain.train as training


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostic-splits', required=True)
    args, trainer_args = parser.parse_known_args(argv)
    modern_specs = load_splits(args.diagnostic_splits, 32)
    if not modern_specs:
        parser.error('Diagnostic suite is empty')
    original = training.evaluate

    def evaluate(cfg, ppo, featurizer, images, specs, device, **kwargs):
        cards = configured_cards(cfg['env'])
        assert not ({s.card for s in specs} & {s.card for s in modern_specs})
        assert all(s.card in images for s in modern_specs)
        started = time.perf_counter()
        legacy = original(cfg, ppo, featurizer, images, specs, device, include_records=True)
        print('LEGACY_TH06', json.dumps(legacy['overall']), flush=True)
        diagnostic_cfg = copy.deepcopy(cfg)
        diagnostic_cfg['eval']['intent'] = 'follow_player_v1'
        diagnostic_cfg['env']['warmup_max'] = 0
        diagnostic_cfg['env']['max_frames'] = max(
            int(cards[s.card].meta['time_limit']) + 300 for s in modern_specs)
        modern = original(diagnostic_cfg, ppo, featurizer, images, modern_specs,
                          device, include_records=True)
        modern['legacy_th06'] = legacy
        modern['diagnostic_protocol'] = {
            'splits': args.diagnostic_splits, 'intent': 'follow_player_v1',
            'warmup_max': 0, 'max_frames': diagnostic_cfg['env']['max_frames'],
            'training_cards_retained': True, 'hard_is_training_difficulty': True,
            'lunatic_is_difficulty_generalization': True,
            'best_selection': 'modern_overall',
            'wall_seconds_including_legacy': time.perf_counter() - started,
        }
        modern['by_source'] = {
            source: summarize_eval([r for r in modern['records']
                                    if cards[r['card']].meta['source'] == source])
            for source in sorted({cards[s.card].meta['source'] for s in modern_specs})
        }
        print('MODERN_BY_SOURCE', json.dumps(modern['by_source']), flush=True)
        return modern

    training.evaluate = evaluate
    try:
        return training.main(trainer_args)
    finally:
        training.evaluate = original


if __name__ == '__main__':
    raise SystemExit(main())
