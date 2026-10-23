# Booster K1 + LAFAN1 + HoloMotion workspace

This worktree is reserved for adapting HoloMotion motion-tracking training to
the Booster K1 22-DoF robot.

## Directory map

- `data/lafan1_raw_bvh/`
  - 77 original LAFAN1 BVH clips copied from the local GMR workspace.
  - This directory is ignored by Git because motion datasets must not be
    committed to the HoloMotion source repository.
- `data/lafan1_holosmpl_formal_h5/`
  - LAFAN1 already converted to HoloSMPL formal H5.
  - Contains one shard and its manifest; this is human-side motion data, not
    robot-side K1 training data.
- `tools/booster_k1_retarget/`
  - Existing GMR implementation and K1 assets.
  - Existing LAFAN/SMPL-X dataset conversion scripts.
  - The `retarget_selected_reference_gmr.py` wrapper and official-K1 mapping
    configs copied from the locally validated K1 moonwalk work.
- `assets/robots/booster_k1/`
  - Official Booster Assets K1 22-DoF URDF/MJCF and meshes.
- `references/booster_train_k1/`
  - Booster Train Isaac Lab code retained as a reference for K1 articulation,
    actuator, joint-order, observation, action, and reward settings.

## Current compatibility status

### Completed

1. Added the official Booster K1 22-DoF URDF/MJCF assets and a dedicated
   Isaac Lab robot configuration with verified joint order.
2. Retargeted LaFAN1 directly from BVH/GMR to K1 robot HDF5 v2:
   - training: Subjects 1-4;
   - validation: Subject 5.
3. Added the dedicated training config
   `motion_tracking_booster_k1_lafan.yaml`.
4. Made reference kinematics and actor observation construction support a
   robot-specific DoF count instead of assuming G1's 29 joints.
5. Added K1-specific reward points, PPO auxiliary bodies, mass/COM
   randomization bodies, and curriculum body names.
6. Excluded all `obstacles*` clips from the flat/rough-terrain baseline without
   deleting them from the source HDF5 datasets.
7. Reduced the initial K1 actor to 16 routed experts and a 256-wide
   Transformer; reduced the critic to `[1024, 1024, 512]`.
8. Updated the training launcher to import this workspace before any other
   editable HoloMotion checkout.
9. Played all 13 Subject-5 validation motions in the K1 MuJoCo viewer.
10. Reached the PPO training loop with the resolved runtime contract:
    - actor observation: 506 values;
    - action output: 22 values;
    - actor parameters: 3.094M;
    - critic parameters: 2.442M.
11. Completed the 10,000-iteration K1 LaFAN training run and saved
    `model_9999.pt` plus `exported/model_9999.onnx`.
12. Added a K1 training-set offline rollout entry and a desktop comparison
    viewer. The viewer has a searchable clip list, synchronized reference and
    policy playback, a timeline, and MP4 recording/export.

### Still required

1. Generate full training-set policy rollouts for `model_9999` and inspect
   them with the desktop comparison viewer.
2. Add a K1 evaluation path with full validation-clip coverage. The existing
   HoloMotion MuJoCo sim-to-sim wrapper is G1-specific and remains disabled.
3. Validate the exported ONNX policy in a K1-aware runtime; export itself has
   completed, but the existing MuJoCo sim-to-sim wrapper is still G1-specific.
4. Add K1 deployment/runtime support only after simulation evaluation passes.
5. Build matched stair/obstacle scenes before using the retained
   `obstacles*` clips for training or evaluation.
6. The AIST++ dance conversion is prepared but intentionally paused; the SMPL
   archive is downloaded, while dance retargeting and QA have not been run.

## Training-set policy comparison viewer

First generate policy rollouts from the training HDF5 dataset. The default
checkpoint is the completed `model_9999.pt`; the K1 launcher explicitly puts
this worktree first on `PYTHONPATH` and uses a 20,000-frame ceiling so LaFAN
clips are not split into colliding output names.

```bash
bash holomotion/scripts/evaluation/eval_booster_k1_training_set.sh
```

To generate only selected clips, provide a Hydra list literal:

```bash
MOTION_NAMES="['walk1_subject1','dance1_subject1']" \
  bash holomotion/scripts/evaluation/eval_booster_k1_training_set.sh
```

The evaluation log prints the resulting
`isaaclab_eval_output_model_9999_<dataset>` directory. Open the desktop viewer
with that directory:

```bash
POLICY_NPZ_DIR="logs/HoloMotionBoosterK1LaFAN/20261009_092900-motion_tracking_booster_k1_lafan/isaaclab_eval_output_model_9999_lafan1_booster_k1_gmr_h5_train_subject1_4" \
  bash holomotion/scripts/evaluation/view_booster_k1_training_comparison.sh
```

The left sidebar selects a training clip manually. The main panel shows the
complete HDF5 training reference on the left and the Isaac Lab policy rollout
on the right. `开始录像` records the viewed playback; `导出完整切片` renders the
whole selected comparison to MP4 under `comparison_videos/`.

Do not point the K1 training config at a G1 29-DoF HDF5 dataset. Matching file
names or array names do not make the reference joint order compatible.

## Provenance

- Raw LAFAN1 source: `/home/tcl/robot_projects/GMR/lafan1`
- HoloSMPL formal H5 source:
  `/home/tcl/Desktop/start/eval_campaign/holomotion/intermediate/formal_h5`
- GMR source: `/home/tcl/robot_projects/GMR`
- Validated K1 wrapper/config source:
  `/home/tcl/Desktop/start/dance-evaluator and tracker/k1_moonwalk`
- Official K1 asset and Booster Train source:
  `k1_moonwalk/upstream/booster_assets` and
  `k1_moonwalk/upstream/booster_train`

No old K1 logs, checkpoints, videos, rollouts, or generated evaluation outputs
were copied.
