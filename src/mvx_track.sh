#!/bin/bash
##DET_PATH refers to a detection txt file path
##GT_CLEAR_PATH refers to gt txt file path which would be used for CLEAR MOT metric calculating
##PRED_FOLDER refers to folder where you choose to save your track results and visualize results
# DET_PATH='/home/lizirui/det_results/test_wild.txt'
# DET_PATH='/home/lizirui/det_results/test(1).txt'
# DET_PATH='/home/lizirui/det_results/Tracktacular/mvx/bevformer.txt'
DET_PATH='/home/lizirui/det_results/MVOT/mvot-multiviewx.txt'
GT_CLEAR_PATH='/home/lizirui/gt/MultiviewX/CLEAR/mota_gt.txt'
# PRED_FOLDER='/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/wild_results'
# PRED_FOLDER='/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/mvx_results'
PRED_FOLDER='/home/lizirui/MVSORT/src/mvx_results/'
python3 /home/lizirui/MVSORT/src/track.py \
 --det_path $DET_PATH --output_folder $PRED_FOLDER --eval multiviewx \
  --gt $GT_CLEAR_PATH --exp_name mota_pred --cfg /home/lizirui/MVSORT/src/configs/multiviewx.yml
## you can eval HOTA and related metrics using the following script, 
## before doing that, you should make sure the parameter in the script is correctly set for your dataset
# sh /home/lizirui/MVdetr/multiview_detector/evaluation/TrackEval/evalHOTA.sh