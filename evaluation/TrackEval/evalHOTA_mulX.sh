python ./run/run_multiviewx.py \
 --BENCHMARK MOT17 --TRACKERS_TO_EVAL mota_pred_HOTA.txt --GT_TO_EVAL gt.txt \
 --GT_FOLDER  /home/lizirui/gt/MultiviewX/HOTA --TRACKERS_FOLDER /home/lizirui/MVSORT/src/mvx_results/ \
 --METRICS CLEAR HOTA --USE_PARALLEL False --NUM_PARALLEL_CORES 1  