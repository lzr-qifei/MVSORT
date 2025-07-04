# from multiview_detector.evaluation.eval_mot import mot_metrics
import motmetrics as mm
import numpy as np
import datetime
import pytz
import os

# 获取当前时间，并设置为北京时间（UTC+8）
beijing_tz = pytz.timezone('Asia/Shanghai')
current_time = datetime.datetime.now(beijing_tz)

# 获取当前时间
# current_time = datetime.datetime.now()

# 格式化时间
formatted_time = current_time.strftime("%m-%d-%H-%M")

def mot_metrics_wild(tSource, gtSource,output_folder, scale=0.025):
    gt = np.loadtxt(gtSource, delimiter=',')
    dt = np.loadtxt(tSource, delimiter=',')

    accs = []
    frame_id = 1800
    false_positives_per_frame = []
    for seq in np.unique(gt[:, 0]).astype(int):
        acc = mm.MOTAccumulator()
        for frame in np.unique(gt[:, 1]).astype(int):
            gt_dets = gt[np.logical_and(gt[:, 0] == seq, gt[:, 1] == frame)][:, (2, 8, 9)]
            dt_dets = dt[np.logical_and(dt[:, 0] == seq, dt[:, 1] == frame)][:, (2, 8, 9)]

            # format: gt, t
            C = mm.distances.norm2squared_matrix(gt_dets[:, 1:3] * scale, dt_dets[:, 1:3] * scale)
            C = np.sqrt(C)

            acc.update(gt_dets[:, 0].astype('int').tolist(),
                       dt_dets[:, 0].astype('int').tolist(),
                       C,
                       frameid=frame)
            
            events = acc.events.loc[frame_id]
            num_false_positives = events[events.Type == 'FP'].shape[0]
            false_positives_per_frame.append(num_false_positives)
            frame_id+=5
        accs.append(acc)

    # metrics.compute_metrics(["HOTA"])
    mh = mm.metrics.create()
    # summary = mh.compute_many(accs, metrics=['HOTA'], generate_overall=True)
    summary = mh.compute_many(accs, metrics=mm.metrics.motchallenge_metrics, generate_overall=True)
    summary["motp"] = 1 - summary["motp"]
    print("\n")
    strsummary = mm.io.render_summary(
        summary,
        formatters=mh.formatters,
        namemap=mm.io.motchallenge_metric_names
    )
    print(strsummary)
    import pandas,os
    # summary.to_excel('/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/wild_results/eval_wild'+formatted_time+'.xlsx')
    ex_path = os.path.join(output_folder,f'{formatted_time}.xlsx')
    summary.to_excel(ex_path)

    return
if __name__ =="__main__":
# gt = '/home/lizirui/det_results/mota_wild_test_gt.txt'
# gt = '/home/lizirui/det_results/aa.txt'
    gt = '/home/lizirui/det_results/wild_bev_gt.txt'
    pred = '/home/lizirui/det_results/wild_mvdetr_sort/pred_40_track_result.txt'
    mot_metrics_wild(pred,gt,os.path.dirname(pred),scale=0.4)