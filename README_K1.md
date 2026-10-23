# HoloMotion-K1 — current 8-expert code snapshot

Booster K1 adaptation of HorizonRobotics/HoloMotion. This repository preserves
the current local source snapshot, rather than the upstream Git history.
See README.md, LICENSE and NOTICE for upstream installation and attribution.

## Small K1 architecture

- Robot: Booster K1, 22 actuated joints.
- Routed experts: 8; shared experts: 1; Top-K: 2.
- Model width: 256; attention heads: 4; KV heads: 2.
- The 8-expert override is in
  `holomotion/config/training/motion_tracking/motion_tracking_booster_k1_lafan_walk_warmup.yaml`.
- The walk+dance small configuration inherits this architecture through
  `motion_tracking_booster_k1_lafan_walk_dance_joint_reward_small.yaml`.
- The curriculum and clean-small release configurations are included. Older
  medium/16-expert experiment configurations are retained, not the default
  description of this snapshot.

## Included / excluded

Included: policy and PPO code, K1 observation/reward adaptations, training and
evaluation launchers, robot resources, retargeting/repair tools and tests.

Not included: training datasets, checkpoints, generated evaluations, logs,
licensed SMPL/SMPL-X body models, upstream sample motion NPZs or machine secrets.
Dataset paths and checkpoint references in experiment configurations therefore
need to be supplied locally before running those experiments. This is not a
self-contained trained-policy release.

Upstream Git submodule references are preserved. Obtain those dependencies using
`git submodule update --init --recursive` as needed. Respect the separate
licenses and access terms of external assets and models.

## Validation status

This is a source backup of ongoing work, not a claim that the large motion
dataset repair is finished or that all experimental repair tools are production
validated. Source datasets and running repair jobs were not changed by export.
