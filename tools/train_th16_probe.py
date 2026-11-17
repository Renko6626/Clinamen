"""TH16-only MQ4 probe: stop at u500, retain the mixed run's u4000 LR schedule.

Use an empty training holdout; diagnostic cards stay in the training pool.
The checkpoint's experiment metadata records the overridden annealing horizon.
"""
from __future__ import annotations

import argparse
import copy

from stgtrain.cards import configured_cards, load_splits
import stgtrain.train as training

LR_HORIZON = 4000


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostic-splits', default='eval/modern-diagnostic.toml')
    args, trainer_args = parser.parse_known_args(argv)
    diagnostics = [s for s in load_splits(args.diagnostic_splits, 32) if s.card.startswith('th16_')]
    if not diagnostics:
        parser.error('TH16 diagnostic suite is empty')
    original_build, original_eval = training.build_components, training.evaluate
    original_ppo, original_save = training.PPO, training.save_checkpoint

    class MatchedSchedulePPO(original_ppo):
        def train_step(self, container, next_value, iteration, num_iterations, timer=None):
            return super().train_step(container, next_value, iteration, LR_HORIZON, timer=timer)

    def build(cfg, device):
        if (cfg['env']['card_filter']['sources'] != ['th16']
                or cfg['model']['name'] != 'set_attn_mq'
                or cfg['run']['total_updates'] > 500):
            raise ValueError('This probe requires TH16-only MQ4 and at most 500 updates')
        if load_splits(cfg['env']['eval_splits'], cfg['eval']['episodes']):
            raise ValueError('Use an empty training holdout; diagnostics must stay in training')
        images, starts, _, feat, factory = original_build(cfg, device)
        if not {s.card for s in diagnostics} <= {s.image for s in starts}:
            raise ValueError('All TH16 diagnostic cards must remain in training')
        return images, starts, diagnostics, feat, factory

    def evaluate(cfg, ppo, featurizer, images, specs, device, **kwargs):
        cards = configured_cards(cfg['env'])
        c = copy.deepcopy(cfg)
        c['eval']['intent'] = 'follow_player_v1'
        c['env']['warmup_max'] = 0
        c['env']['max_frames'] = max(int(cards[s.card].meta['time_limit']) + 300 for s in specs)
        result = original_eval(c, ppo, featurizer, images, specs, device, include_records=True)
        result['diagnostic_protocol'] = {
            'splits': args.diagnostic_splits, 'source': 'th16', 'intent': 'follow_player_v1',
            'training_cards_retained': True, 'hard_is_training_difficulty': True,
            'lunatic_is_difficulty_generalization': True, 'warmup_max': 0,
            'max_frames': c['env']['max_frames'], 'lr_anneal_updates': LR_HORIZON,
        }
        return result

    def save(path, *, extra=None, **kwargs):
        extra = dict(extra or {})
        extra['experiment'] = {'name': 'th16-mq4-u500', 'lr_anneal_updates': LR_HORIZON,
                               'entrypoint': 'tools/train_th16_probe.py'}
        return original_save(path, extra=extra, **kwargs)

    training.build_components, training.evaluate = build, evaluate
    training.PPO, training.save_checkpoint = MatchedSchedulePPO, save
    try:
        return training.main(trainer_args)
    finally:
        training.build_components, training.evaluate = original_build, original_eval
        training.PPO, training.save_checkpoint = original_ppo, original_save


if __name__ == '__main__':
    raise SystemExit(main())
