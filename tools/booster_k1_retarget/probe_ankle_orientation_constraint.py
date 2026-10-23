"""Minimal isolated foot-orientation ablation; all real joint limits retained."""

import argparse
import json
from pathlib import Path

import mink
import numpy as np

from tools.booster_k1_retarget import compare_lafan_retarget_pipelines as compare
from tools.booster_k1_retarget import retry_guarded_reference as guard
from tools.booster_k1_retarget.recover_short_reference_candidates import dump


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--foot-orientation-cost',type=float,default=0)
    p.add_argument('--ankle-posture-cost',type=float,default=0)
    p.add_argument('--native-cmu-foot-pose',action='store_true')
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    manifest=json.loads((a.case/'input/manifest.json').read_text())
    for c in manifest['clips'].values():c['metadata'].update(actual_foot_orientation_task_override=a.foot_orientation_cost,actual_ankle_posture_cost=a.ankle_posture_cost,native_cmu_foot_pose_override=a.native_cmu_foot_pose,training_approved=False)
    dump(a.output/'input/manifest.json',manifest)
    dump(a.output/'experiment_settings.json',{'base_profile':'old_root_weight','actual_foot_orientation_task_cost':a.foot_orientation_cost,'ankle_posture_cost':a.ankle_posture_cost,'native_cmu_foot_pose':a.native_cmu_foot_pose,'joint_limits_unchanged':True,'source_case':str(a.case.resolve()),'training_approved':False})
    config=json.loads((compare.REPO/'tools/booster_k1_retarget/configs/gmr_smplx_to_official_k1_v2.json').read_text())
    create=guard.probe.create_k1_retargeter
    def make(**kwargs):
        robot=create(**kwargs);retarget=robot.retarget
        frame=0
        if a.native_cmu_foot_pose:
            from tools.booster_k1_retarget.cmu_native_foot_pose import foot_targets
            assert len(manifest['clips'])==1
            clip=next(iter(manifest['clips'].values()))
            desired=foot_targets(clip['metadata'],clip['length'])
            update=robot.update_targets
            def native_targets(*values,**options):
                update(*values,**options)
                for table in [robot.human_body_to_task1,robot.human_body_to_task2]:
                    for side in ['left','right']:
                        task=table[side+'_foot']
                        task.set_target(mink.SE3.from_rotation_and_translation(mink.SO3.from_matrix(desired[side][frame].as_matrix()),task.transform_target_to_world.translation()))
            robot.update_targets=native_targets
        if a.ankle_posture_cost:
            costs=np.zeros(robot.model.nv)
            for j in range(robot.model.njnt):
                if 'ankle' in robot.model.joint(j).name:
                    costs[robot.model.jnt_dofadr[j]]=a.ankle_posture_cost
            for tasks in [robot.tasks1,robot.tasks2]:
                task=mink.PostureTask(robot.model,cost=costs)
                task.set_target(robot.model.qpos0.copy())
                tasks.append(task)
        def override(*values,**options):
            nonlocal frame
            for label,table in [('ik_match_table1',robot.human_body_to_task1),('ik_match_table2',robot.human_body_to_task2)]:
                for name,entry in config[label].items():
                    if 'ankle_roll' in name:table[entry[0]].set_orientation_cost(a.foot_orientation_cost)
            result=retarget(*values,**options)
            frame+=1
            return result
        robot.retarget=override
        return robot
    guard.probe.create_k1_retargeter=make
    compare.worker(argparse.Namespace(output=a.output,worker='old_root_weight',max_frames=10000000))


if __name__=='__main__':main()
