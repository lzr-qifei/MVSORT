##生成MOT格式的gt用于计算HOTA，如果已有可忽略##
python /home/lizirui/MVSORT/evaluation/TrackEval/gt2HOTAgt.py \
    --input /home/lizirui/det_results/earlybird/wild/orig/mota_pred.txt \
    --output /home/lizirui/det_results/earlybird/wild/orig/mota_pred_HOTA.txt