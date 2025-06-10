##生成MOT格式的gt用于计算HOTA，如果已有可忽略##
python /home/lizirui/MVdetr/multiview_detector/evaluation/TrackEval/gt2HOTAgt.py \
    --input /home/lizirui/TrackTacular/mvx_bevformer/mota_pred.txt \
    --output /home/lizirui/TrackTacular/mvx_bevformer/mota_pred_HOTA.txt