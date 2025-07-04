import os
import numpy as np

def iou_batch(bboxes1, bboxes2):
    """
    From SORT: Computes IOU between two bboxes in the form [x1,y1,x2,y2]
    """
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)
    
    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 3], bboxes2[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    o = wh / ((bboxes1[..., 2] - bboxes1[..., 0]) * (bboxes1[..., 3] - bboxes1[..., 1])                                      
        + (bboxes2[..., 2] - bboxes2[..., 0]) * (bboxes2[..., 3] - bboxes2[..., 1]) - wh)                                              
    return(o)  

def dist_batch(detections,trackers):
    distance_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)

    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            distance_matrix[d, t] = np.linalg.norm(det - trk)

    return distance_matrix
import math
def mdist_batch(detections,trackers,covs):
    distance_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)
    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            # distance_matrix[d, t] = np.linalg.norm(det - trk)/covs[t]
            inv_covmat = np.linalg.inv(covs[t])
            x = det - trk
            left_term = np.dot(x, inv_covmat)
            mahal = np.dot(left_term, x.T)
            distance_matrix[d, t] = math.sqrt(mahal)
    return distance_matrix
def save_mdist_results(trackers, covs, output_dir="/home/lizirui/vis_wild"):
    """
    保存mdist_vis函数输出到txt文件
    :param trackers: 跟踪器坐标
    :param covs: 协方差矩阵
    :param output_dir: 输出目录
    """
    import numpy as np
    import os
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取原始输出
    binary_map_e_list, binary_map_m_list = mdist_vis(trackers, covs)
    
    # 保存每个tracker的二值化地图
    for i, (e_map, m_map) in enumerate(zip(binary_map_e_list, binary_map_m_list)):
        # 保存欧氏距离结果
        e_filename = os.path.join(output_dir, f"binary_map_e_{i}.txt")
        np.savetxt(e_filename, 
                  e_map.T.astype(int),  # 转置矩阵保持坐标系一致性
                  fmt='%d', 
                  delimiter=',',
                  header=f'Binary Map E (Tracker {i}) | Shape: {e_map.shape}')

        # 保存马氏距离结果
        m_filename = os.path.join(output_dir, f"binary_map_m_{i}.txt")
        np.savetxt(m_filename,
                  m_map.T.astype(int),
                  fmt='%d',
                  delimiter=',',
                  header=f'Binary Map M (Tracker {i}) | Shape: {m_map.shape}')
        
    print(f"Saved {len(binary_map_e_list)} pairs of maps to {output_dir}")

# def mdist_vis(trackers,covs):
#     height = 1440
#     width = 480
#     distance_threshold = 100
#     m_distance_threshold = 100
#     # 生成所有点的坐标
#     detections = np.array([[x, y] for y in range(height) for x in range(width)])
#     binary_map_e_list = []
#     binary_map_m_list = []

#     # 计算距离并判断是否满足阈值
#     for t,trk in enumerate(trackers):
#         binary_map_e = np.zeros((width,height ), dtype=bool)
#         binary_map_m = np.zeros((width,height ), dtype=bool)
#         # det_copy = detections.copy()
#         m_dist_map = np.zeros((width,height ))
#         e_dist_map = np.zeros((width,height ))
#         # distances_e = np.linalg.norm(detections - trk, axis=1)  # 计算欧几里得距离
#         # distances_e = distances_e.reshape(height, width)  # 将距离结果重塑为地图形状
        
#         for det in detections:
#             inv_covmat = np.linalg.inv(covs[t])
#             det_x = np.append(det,[0,0])
#             x = det_x -trk
#             left_term = np.dot(x, inv_covmat)
#             mahal = np.dot(left_term, x.T)
#             # print(det)
#             try:
#                 # print(det)
#                 m_dist_map[det[0],det[1]] = math.sqrt(mahal)
#                 # print(det)
#                 e_dist_map[det[0],det[1]] = np.linalg.norm(det - trk[:2], axis=0)
#                 # print(detections)
#             except:
#                 print(detections)
#                 print(det)
#                 return None
#         print(m_dist_map)
#         binary_map_m |= (m_dist_map <= m_distance_threshold)
#         binary_map_e |= (e_dist_map <= distance_threshold)  # 更新二值化地图
#         binary_map_e_list.append(binary_map_e)
#         binary_map_m_list.append(binary_map_m)
#         if t>=4:
#             return binary_map_e_list, binary_map_m_list
#     return binary_map_e_list, binary_map_m_list

        # distances_m = 

     
def CMD_batch(detections,trackers,covs,m_noise):
    H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
    distance_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)
    for d,det in enumerate(detections):
        for t,trk in enumerate(trackers):
            epsi = det - trk
            r = np.dot(H.T,np.dot(m_noise[t],H))
            S = covs[t] + r
            S_d = np.linalg.det(S)
            S_d = math.log(S_d)
            inv_covmat = np.linalg.inv(S)
            left_term = np.dot(epsi, inv_covmat)
            mahal = np.dot(left_term, epsi.T) + S_d
            distance_matrix[d, t] = math.sqrt(mahal)
    return distance_matrix


            

def giou_batch(bboxes1, bboxes2):
    """
    :param bbox_p: predict of bbox(N,4)(x1,y1,x2,y2)
    :param bbox_g: groundtruth of bbox(N,4)(x1,y1,x2,y2)
    :return:
    """
    # for details should go to https://arxiv.org/pdf/1902.09630.pdf
    # ensure predict's bbox form
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)

    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 3], bboxes2[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    union = ((bboxes1[..., 2] - bboxes1[..., 0]) * (bboxes1[..., 3] - bboxes1[..., 1])                                      
        + (bboxes2[..., 2] - bboxes2[..., 0]) * (bboxes2[..., 3] - bboxes2[..., 1]) - wh)  
    iou = wh / union

    xxc1 = np.minimum(bboxes1[..., 0], bboxes2[..., 0])
    yyc1 = np.minimum(bboxes1[..., 1], bboxes2[..., 1])
    xxc2 = np.maximum(bboxes1[..., 2], bboxes2[..., 2])
    yyc2 = np.maximum(bboxes1[..., 3], bboxes2[..., 3])
    wc = xxc2 - xxc1 
    hc = yyc2 - yyc1 
    assert((wc > 0).all() and (hc > 0).all())
    area_enclose = wc * hc 
    giou = iou - (area_enclose - union) / area_enclose
    giou = (giou + 1.)/2.0 # resize from (-1,1) to (0,1)
    return giou


def diou_batch(bboxes1, bboxes2):
    """
    :param bbox_p: predict of bbox(N,4)(x1,y1,x2,y2)
    :param bbox_g: groundtruth of bbox(N,4)(x1,y1,x2,y2)
    :return:
    """
    # for details should go to https://arxiv.org/pdf/1902.09630.pdf
    # ensure predict's bbox form
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)

    # calculate the intersection box
    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 3], bboxes2[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    union = ((bboxes1[..., 2] - bboxes1[..., 0]) * (bboxes1[..., 3] - bboxes1[..., 1])                                      
        + (bboxes2[..., 2] - bboxes2[..., 0]) * (bboxes2[..., 3] - bboxes2[..., 1]) - wh) 
    iou = wh / union
    centerx1 = (bboxes1[..., 0] + bboxes1[..., 2]) / 2.0
    centery1 = (bboxes1[..., 1] + bboxes1[..., 3]) / 2.0
    centerx2 = (bboxes2[..., 0] + bboxes2[..., 2]) / 2.0
    centery2 = (bboxes2[..., 1] + bboxes2[..., 3]) / 2.0

    inner_diag = (centerx1 - centerx2) ** 2 + (centery1 - centery2) ** 2

    xxc1 = np.minimum(bboxes1[..., 0], bboxes2[..., 0])
    yyc1 = np.minimum(bboxes1[..., 1], bboxes2[..., 1])
    xxc2 = np.maximum(bboxes1[..., 2], bboxes2[..., 2])
    yyc2 = np.maximum(bboxes1[..., 3], bboxes2[..., 3])

    outer_diag = (xxc2 - xxc1) ** 2 + (yyc2 - yyc1) ** 2
    diou = iou - inner_diag / outer_diag

    return (diou + 1) / 2.0 # resize from (-1,1) to (0,1)

def ciou_batch(bboxes1, bboxes2):
    """
    :param bbox_p: predict of bbox(N,4)(x1,y1,x2,y2)
    :param bbox_g: groundtruth of bbox(N,4)(x1,y1,x2,y2)
    :return:
    """
    # for details should go to https://arxiv.org/pdf/1902.09630.pdf
    # ensure predict's bbox form
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)

    # calculate the intersection box
    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 3], bboxes2[..., 3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    union = ((bboxes1[..., 2] - bboxes1[..., 0]) * (bboxes1[..., 3] - bboxes1[..., 1])                                      
        + (bboxes2[..., 2] - bboxes2[..., 0]) * (bboxes2[..., 3] - bboxes2[..., 1]) - wh) 
    iou = wh / union

    centerx1 = (bboxes1[..., 0] + bboxes1[..., 2]) / 2.0
    centery1 = (bboxes1[..., 1] + bboxes1[..., 3]) / 2.0
    centerx2 = (bboxes2[..., 0] + bboxes2[..., 2]) / 2.0
    centery2 = (bboxes2[..., 1] + bboxes2[..., 3]) / 2.0

    inner_diag = (centerx1 - centerx2) ** 2 + (centery1 - centery2) ** 2

    xxc1 = np.minimum(bboxes1[..., 0], bboxes2[..., 0])
    yyc1 = np.minimum(bboxes1[..., 1], bboxes2[..., 1])
    xxc2 = np.maximum(bboxes1[..., 2], bboxes2[..., 2])
    yyc2 = np.maximum(bboxes1[..., 3], bboxes2[..., 3])

    outer_diag = (xxc2 - xxc1) ** 2 + (yyc2 - yyc1) ** 2
    
    w1 = bboxes1[..., 2] - bboxes1[..., 0]
    h1 = bboxes1[..., 3] - bboxes1[..., 1]
    w2 = bboxes2[..., 2] - bboxes2[..., 0]
    h2 = bboxes2[..., 3] - bboxes2[..., 1]

    # prevent dividing over zero. add one pixel shift
    h2 = h2 + 1.
    h1 = h1 + 1.
    arctan = np.arctan(w2/h2) - np.arctan(w1/h1)
    v = (4 / (np.pi ** 2)) * (arctan ** 2)
    S = 1 - iou 
    alpha = v / (S+v)
    ciou = iou - inner_diag / outer_diag - alpha * v
    
    return (ciou + 1) / 2.0 # resize from (-1,1) to (0,1)


def ct_dist(bboxes1, bboxes2):
    """
        Measure the center distance between two sets of bounding boxes,
        this is a coarse implementation, we don't recommend using it only
        for association, which can be unstable and sensitive to frame rate
        and object speed.
    """
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)

    centerx1 = (bboxes1[..., 0] + bboxes1[..., 2]) / 2.0
    centery1 = (bboxes1[..., 1] + bboxes1[..., 3]) / 2.0
    centerx2 = (bboxes2[..., 0] + bboxes2[..., 2]) / 2.0
    centery2 = (bboxes2[..., 1] + bboxes2[..., 3]) / 2.0

    ct_dist2 = (centerx1 - centerx2) ** 2 + (centery1 - centery2) ** 2

    ct_dist = np.sqrt(ct_dist2)

    # The linear rescaling is a naive version and needs more study
    ct_dist = ct_dist / ct_dist.max()
    return ct_dist.max() - ct_dist # resize to (0,1)



def speed_direction_batch(dets, tracks):
    tracks = tracks[..., np.newaxis]
    CX1, CY1 = (dets[:,0] )/2.0, (dets[:,1])/2.0
    CX2, CY2 = (tracks[:,0] ) /2.0, (tracks[:,1])/2.0
    dx = CX1 - CX2 
    dy = CY1 - CY2 
    norm = np.sqrt(dx**2 + dy**2) + 1e-6
    dx = dx / norm 
    dy = dy / norm
    return dy, dx # size: num_track x num_det


def linear_assignment(cost_matrix):
    try:
        import lap
        _, x, y = lap.lapjv(cost_matrix, extend_cost=True)
        return np.array([[y[i],i] for i in x if i >= 0]) #
    except ImportError:
        from scipy.optimize import linear_sum_assignment
        x, y = linear_sum_assignment(cost_matrix)
        return np.array(list(zip(x, y)))


def associate_detections_to_trackers(detections,trackers,dist_threshold = 50):
    """
    Assigns detections to tracked object (both represented as bounding boxes)
    Returns 3 lists of matches, unmatched_detections and unmatched_trackers
    """
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,3),dtype=int)

    # iou_matrix = iou_batch(detections, trackers)
    dist_matrix = dist_batch(detections, trackers)

    if min(dist_matrix.shape) > 0:
        a = (dist_matrix > dist_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = linear_assignment(-dist_matrix)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    #filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(dist_matrix[m[0], m[1]]<dist_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


def associate(detections, trackers, dist_threshold , velocities, previous_obs, vdc_weight):    
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,3),dtype=int)

    Y, X = speed_direction_batch(detections, previous_obs)
    inertia_Y, inertia_X = velocities[:,0], velocities[:,1]
    inertia_Y = np.repeat(inertia_Y[:, np.newaxis], Y.shape[1], axis=1)
    inertia_X = np.repeat(inertia_X[:, np.newaxis], X.shape[1], axis=1)
    diff_angle_cos = inertia_X * X + inertia_Y * Y
    diff_angle_cos = np.clip(diff_angle_cos, a_min=-1, a_max=1)
    diff_angle = np.arccos(diff_angle_cos)
    diff_angle = (np.pi /2.0 - np.abs(diff_angle)) / np.pi

    valid_mask = np.ones(previous_obs.shape[0])
    valid_mask[np.where(previous_obs[:,2]<0)] = 0
    
    # iou_matrix = iou_batch(detections, trackers)
    dist_matrix = dist_batch(detections, trackers)
    scores = np.repeat(detections[:,-1][:, np.newaxis], trackers.shape[0], axis=1)
    dist_matrix = dist_matrix * scores
    # iou_matrix = iou_matrix * scores # a trick sometiems works, we don't encourage this
    valid_mask = np.repeat(valid_mask[:, np.newaxis], X.shape[1], axis=1)

    angle_diff_cost = (valid_mask * diff_angle) * vdc_weight
    angle_diff_cost = angle_diff_cost.T
    angle_diff_cost = angle_diff_cost * scores

    if min(dist_matrix.shape) > 0:
        a = (dist_matrix < dist_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            # X_min = np.min(dist_matrix)
            # X_max = np.max(dist_matrix)
            # X_norm = (dist_matrix - X_min) / (X_max - X_min) *10
            # matched_indices = linear_assignment((X_norm+angle_diff_cost))
            matched_indices = linear_assignment((dist_matrix+angle_diff_cost))
            # print(angle_diff_cost)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(dist_matrix[m[0], m[1]] > dist_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers),dist_matrix


def associate_new(detections, trackers, dist_threshold , velocities, previous_obs, vdc_weight,
covs,dets_x,trks_x):    
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,3),dtype=int)

    Y, X = speed_direction_batch(detections, previous_obs)
    inertia_Y, inertia_X = velocities[:,0], velocities[:,1]
    inertia_Y = np.repeat(inertia_Y[:, np.newaxis], Y.shape[1], axis=1)
    inertia_X = np.repeat(inertia_X[:, np.newaxis], X.shape[1], axis=1)
    diff_angle_cos = inertia_X * X + inertia_Y * Y
    diff_angle_cos = np.clip(diff_angle_cos, a_min=-1, a_max=1)
    diff_angle = np.arccos(diff_angle_cos)
    diff_angle = (np.pi /2.0 - np.abs(diff_angle)) / np.pi

    valid_mask = np.ones(previous_obs.shape[0])
    valid_mask[np.where(previous_obs[:,2]<0)] = 0
    
    # iou_matrix = iou_batch(detections, trackers)
    
    dist_matrix = mdist_batch(dets_x,trks_x,covs)
    # ###test ####
    # def visual(mat,path):
    #     import matplotlib.pyplot as plt
    #     import seaborn as sns
    #     import numpy as np

    #     # 示例二维矩阵：目标A和目标B之间的距离
    #     # distance_matrix = np.array([[2.5, 3.0, 4.5], [1.2, 2.3, 3.8], [4.0, 2.1, 3.6]])

    #     # 创建热力图
    #     plt.figure(figsize=(8, 6))  # 设置图像大小
    #     sns.heatmap(mat, annot=False, cmap='coolwarm', fmt='.2f', cbar_kws={'label': 'Distance'})

    #     # 添加标题和标签
    #     plt.title('Distance Matrix between Target A and Target B')
    #     plt.xlabel('Target B Points')
    #     plt.ylabel('Target A Points')

    #     # 保存图像为文件
    #     plt.savefig(path, dpi=300, bbox_inches='tight')  # 保存为PNG文件，dpi=300为高质量，bbox_inches='tight'去除空白
    #     return
    #     # 显示图像
    #     # plt.show()
    # dist_matrix_ori = dist_batch(detections, trackers)
    # path1 = '/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/results/ori.png'
    # path2 = '/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/results/new.png'
    # diff = dist_matrix - dist_matrix_ori
    # if diff.sum()!=0:
        # print(dist_matrix.mean())
        # visual(dist_matrix_ori,path1)
        # visual(dist_matrix,path2)
    ############
    scores = np.repeat(detections[:,-1][:, np.newaxis], trackers.shape[0], axis=1)
    # dist_matrix = dist_matrix * scores
    # iou_matrix = iou_matrix * scores # a trick sometiems works, we don't encourage this
    valid_mask = np.repeat(valid_mask[:, np.newaxis], X.shape[1], axis=1)

    angle_diff_cost = (valid_mask * diff_angle) * vdc_weight
    angle_diff_cost = angle_diff_cost.T
    # angle_diff_cost = angle_diff_cost * scores

    if min(dist_matrix.shape) > 0:
        a = (dist_matrix < dist_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            # X_min = np.min(dist_matrix)
            # X_max = np.max(dist_matrix)
            # X_norm = (dist_matrix - X_min) / (X_max - X_min) *10
            # matched_indices = linear_assignment((X_norm+angle_diff_cost))
            matched_indices = linear_assignment((dist_matrix+angle_diff_cost))
            # print(angle_diff_cost)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(dist_matrix[m[0], m[1]] > dist_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers),dist_matrix
def associate_opposite(detections, trackers, dist_threshold , velocities, previous_obs, vdc_weight,
covs,dets_x,trks_x):    
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,3),dtype=int)

    Y, X = speed_direction_batch(detections, previous_obs)
    inertia_Y, inertia_X = velocities[:,0], velocities[:,1]
    inertia_Y = np.repeat(inertia_Y[:, np.newaxis], Y.shape[1], axis=1)
    inertia_X = np.repeat(inertia_X[:, np.newaxis], X.shape[1], axis=1)
    diff_angle_cos = inertia_X * X + inertia_Y * Y
    diff_angle_cos = np.clip(diff_angle_cos, a_min=-1, a_max=1)
    diff_angle = np.arccos(diff_angle_cos)
    diff_angle = (np.pi /2.0 - np.abs(diff_angle)) / np.pi

    valid_mask = np.ones(previous_obs.shape[0])
    valid_mask[np.where(previous_obs[:,2]<0)] = 0
    
    # iou_matrix = iou_batch(detections, trackers)
    
    dist_matrix = mdist_batch(dets_x,trks_x,covs)
    scores = np.repeat(detections[:,-1][:, np.newaxis], trackers.shape[0], axis=1)
    # dist_matrix = dist_matrix * scores
    # iou_matrix = iou_matrix * scores # a trick sometiems works, we don't encourage this
    valid_mask = np.repeat(valid_mask[:, np.newaxis], X.shape[1], axis=1)

    angle_diff_cost = (valid_mask * diff_angle) * vdc_weight
    angle_diff_cost = angle_diff_cost.T
    # angle_diff_cost = angle_diff_cost * scores

    if min(dist_matrix.shape) > 0:
        a = (dist_matrix < dist_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            # X_min = np.min(dist_matrix)
            # X_max = np.max(dist_matrix)
            # X_norm = (dist_matrix - X_min) / (X_max - X_min) *10
            # matched_indices = linear_assignment((X_norm+angle_diff_cost))
            matched_indices = linear_assignment((-dist_matrix+angle_diff_cost))
            # print(angle_diff_cost)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(dist_matrix[m[0], m[1]] < dist_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers),dist_matrix
def associate_CMD(detections, trackers, dist_threshold , velocities, previous_obs, vdc_weight,
covs,m_noise,dets_x,trks_x):    
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,3),dtype=int)

    Y, X = speed_direction_batch(detections, previous_obs)
    inertia_Y, inertia_X = velocities[:,0], velocities[:,1]
    inertia_Y = np.repeat(inertia_Y[:, np.newaxis], Y.shape[1], axis=1)
    inertia_X = np.repeat(inertia_X[:, np.newaxis], X.shape[1], axis=1)
    diff_angle_cos = inertia_X * X + inertia_Y * Y
    diff_angle_cos = np.clip(diff_angle_cos, a_min=-1, a_max=1)
    diff_angle = np.arccos(diff_angle_cos)
    diff_angle = (np.pi /2.0 - np.abs(diff_angle)) / np.pi

    valid_mask = np.ones(previous_obs.shape[0])
    valid_mask[np.where(previous_obs[:,2]<0)] = 0
    
    # iou_matrix = iou_batch(detections, trackers)
    
    dist_matrix = CMD_batch(dets_x,trks_x,covs,m_noise)
    # histogram.add_matrix(dist_matrix)
    # ###test ####
    # def visual(mat,path):
    #     import matplotlib.pyplot as plt
    #     import seaborn as sns
    #     import numpy as np

    #     # 示例二维矩阵：目标A和目标B之间的距离
    #     # distance_matrix = np.array([[2.5, 3.0, 4.5], [1.2, 2.3, 3.8], [4.0, 2.1, 3.6]])

    #     # 创建热力图
    #     plt.figure(figsize=(8, 6))  # 设置图像大小
    #     sns.heatmap(mat, annot=False, cmap='coolwarm', fmt='.2f', cbar_kws={'label': 'Distance'})

    #     # 添加标题和标签
    #     plt.title('Distance Matrix between Target A and Target B')
    #     plt.xlabel('Target B Points')
    #     plt.ylabel('Target A Points')

    #     # 保存图像为文件
    #     plt.savefig(path, dpi=300, bbox_inches='tight')  # 保存为PNG文件，dpi=300为高质量，bbox_inches='tight'去除空白
    #     return
    #     # 显示图像
    #     # plt.show()
    # dist_matrix_ori = dist_batch(detections, trackers)
    # path1 = '/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/results/ori.png'
    # path2 = '/home/lizirui/MVdetr/multiview_detector/tracker/OC_SORT/results/new.png'
    # diff = dist_matrix - dist_matrix_ori
    # if diff.sum()!=0:
        # print(dist_matrix.mean())
        # visual(dist_matrix_ori,path1)
        # visual(dist_matrix,path2)
    ############
    scores = np.repeat(detections[:,-1][:, np.newaxis], trackers.shape[0], axis=1)
    # dist_matrix = dist_matrix * scores
    # iou_matrix = iou_matrix * scores # a trick sometiems works, we don't encourage this
    valid_mask = np.repeat(valid_mask[:, np.newaxis], X.shape[1], axis=1)

    angle_diff_cost = (valid_mask * diff_angle) * vdc_weight
    angle_diff_cost = angle_diff_cost.T
    # angle_diff_cost = angle_diff_cost * scores

    if min(dist_matrix.shape) > 0:
        a = (dist_matrix < dist_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            # X_min = np.min(dist_matrix)
            # X_max = np.max(dist_matrix)
            # X_norm = (dist_matrix - X_min) / (X_max - X_min) *10
            # matched_indices = linear_assignment((X_norm+angle_diff_cost))
            matched_indices = linear_assignment((dist_matrix+angle_diff_cost))
            # print(angle_diff_cost)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(dist_matrix[m[0], m[1]] > dist_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers),dist_matrix

def associate_kitti(detections, trackers, det_cates, iou_threshold, 
        velocities, previous_obs, vdc_weight):
    if(len(trackers)==0):
        return np.empty((0,2),dtype=int), np.arange(len(detections)), np.empty((0,5),dtype=int)

    """
        Cost from the velocity direction consistency
    """
    Y, X = speed_direction_batch(detections, previous_obs)
    inertia_Y, inertia_X = velocities[:,0], velocities[:,1]
    inertia_Y = np.repeat(inertia_Y[:, np.newaxis], Y.shape[1], axis=1)
    inertia_X = np.repeat(inertia_X[:, np.newaxis], X.shape[1], axis=1)
    diff_angle_cos = inertia_X * X + inertia_Y * Y
    diff_angle_cos = np.clip(diff_angle_cos, a_min=-1, a_max=1)
    diff_angle = np.arccos(diff_angle_cos)
    diff_angle = (np.pi /2.0 - np.abs(diff_angle)) / np.pi

    valid_mask = np.ones(previous_obs.shape[0])
    valid_mask[np.where(previous_obs[:,4]<0)]=0  
    valid_mask = np.repeat(valid_mask[:, np.newaxis], X.shape[1], axis=1)

    scores = np.repeat(detections[:,-1][:, np.newaxis], trackers.shape[0], axis=1)
    angle_diff_cost = (valid_mask * diff_angle) * vdc_weight
    angle_diff_cost = angle_diff_cost.T
    angle_diff_cost = angle_diff_cost * scores

    """
        Cost from IoU
    """
    iou_matrix = iou_batch(detections, trackers)
    

    """
        With multiple categories, generate the cost for catgory mismatch
    """
    num_dets = detections.shape[0]
    num_trk = trackers.shape[0]
    cate_matrix = np.zeros((num_dets, num_trk))
    for i in range(num_dets):
            for j in range(num_trk):
                if det_cates[i] != trackers[j, 4]:
                        cate_matrix[i][j] = -1e6
    
    cost_matrix = - iou_matrix -angle_diff_cost - cate_matrix

    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            matched_indices = linear_assignment(cost_matrix)
    else:
        matched_indices = np.empty(shape=(0,2))

    unmatched_detections = []
    for d, det in enumerate(detections):
        if(d not in matched_indices[:,0]):
            unmatched_detections.append(d)
    unmatched_trackers = []
    for t, trk in enumerate(trackers):
        if(t not in matched_indices[:,1]):
            unmatched_trackers.append(t)

    #filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if(iou_matrix[m[0], m[1]]<iou_threshold):
            unmatched_detections.append(m[0])
            unmatched_trackers.append(m[1])
        else:
            matches.append(m.reshape(1,2))
    if(len(matches)==0):
        matches = np.empty((0,2),dtype=int)
    else:
        matches = np.concatenate(matches,axis=0)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)