import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
import math
import os


def mdist_vis(trackers, covs):
    """
    Efficiently compute Mahalanobis and Euclidean distance maps for multiple trackers.
    
    Args:
        trackers (np.ndarray): Array of tracker positions
        covs (np.ndarray): Covariance matrices for each tracker
    
    Returns:
        tuple: Lists of binary maps for Euclidean and Mahalanobis distances
    """
    height, width = 1440, 480
    distance_threshold = 80
    m_distance_threshold = 35
    
    # Vectorized coordinate generation
    x_coords = np.arange(width)
    y_coords = np.arange(height)
    xx, yy = np.meshgrid(x_coords, y_coords)
    detections = np.column_stack([xx.ravel(), yy.ravel()]).astype(float)
    
    binary_map_e_list = []
    binary_map_m_list = []

    # Vectorized distance calculation
    for t, (trk, cov) in enumerate(zip(trackers, covs)):
        # Compute inverse covariance matrix
        try:
            inv_covmat = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            print(f"Singular covariance matrix at tracker {t}")
            continue
        
        # Vectorized Mahalanobis distance calculation
        diff = detections - trk[:2]
        diff_extended = np.column_stack([diff, np.zeros((len(diff), 2))])
        
        # Compute Mahalanobis distances
        left_terms = np.dot(diff_extended, inv_covmat)
        mahal_distances = np.sqrt(np.sum(left_terms * diff_extended, axis=1))
        
        # Compute Euclidean distances
        euclidean_distances = np.linalg.norm(diff, axis=1)
        
        # Reshape distance maps
        m_dist_map = mahal_distances.reshape(height, width)
        e_dist_map = euclidean_distances.reshape(height, width)
        
        # Create binary maps
        binary_map_m = m_dist_map <= m_distance_threshold
        binary_map_e = e_dist_map <= distance_threshold
        
        binary_map_e_list.append(binary_map_m)
        binary_map_m_list.append(binary_map_e)
        
        # Early stopping condition
        # if t >= 4:
        #     break
    
    return binary_map_e_list, binary_map_m_list
# def mdist_vis(trackers, covs):
#     height = 1440
#     width = 480
#     distance_threshold = 100
#     m_distance_threshold = 100
    
#     # 生成所有点的坐标
#     detections = np.array([[x, y] for y in range(height) for x in range(width)],dtype=float)
#     binary_map_e_list = []
#     binary_map_m_list = []

#     # 计算距离并判断是否满足阈值
#     for t, trk in enumerate(trackers):
#         binary_map_e = np.zeros((width, height), dtype=bool)
#         binary_map_m = np.zeros((width, height), dtype=bool)
#         m_dist_map = np.zeros((width, height))
#         e_dist_map = np.zeros((width, height))
        
#         for det in detections:
#             inv_covmat = np.linalg.inv(covs[t])
#             det_x = np.append(det, [0, 0])
#             x = det_x - trk
#             left_term = np.dot(x, inv_covmat)
#             mahal = np.dot(left_term, x.T)
            
#             try:
#                 m_dist_map[det[0], det[1]] = math.sqrt(mahal)
#                 e_dist_map[det[0], det[1]] = np.linalg.norm(det - trk[:2], axis=0)
#             except Exception as e:
#                 print(f"Error processing detection: {det}")
#                 print(e)
#                 return None
        
#         binary_map_m |= (m_dist_map <= m_distance_threshold)
#         binary_map_e |= (e_dist_map <= distance_threshold)
#         binary_map_e_list.append(binary_map_e)
#         binary_map_m_list.append(binary_map_m)
        
#         if t >= 4:
#             return binary_map_e_list, binary_map_m_list
    
#     return binary_map_e_list, binary_map_m_list

def visualize_pedestrian_movements(trackers, binary_map_e_list, binary_map_m_list, 
                                   map_size=(1440, 480), 
                                   output_dir='pedestrian_movement_plots', 
                                   file_prefix='pedestrian_movement'):
    """
    可视化行人位置和可移动区域，支持欧几里得和马氏距离，并保存图片
    
    参数:
    - trackers: 行人在地图上的位置列表
    - binary_map_e_list: 欧几里得距离二值化地图列表
    - binary_map_m_list: 马氏距离二值化地图列表
    - map_size: 地图的尺寸，默认为(1440, 480)
    - output_dir: 输出图片的目录
    - file_prefix: 输出文件名前缀
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建子图网格
    fig, axes = plt.subplots(len(trackers), 2, figsize=(20, 5*len(trackers)))
    
    for i, (trk, binary_map_e, binary_map_m) in enumerate(zip(trackers, binary_map_e_list, binary_map_m_list)):
        # 欧几里得距离可移动区域
        axes[i, 0].imshow(binary_map_e.T, cmap='Blues', alpha=0.5)
        axes[i, 0].set_title(f'pedestrian {i+1} - e_distance')
        axes[i, 0].scatter(trk[1], trk[0], color='red', s=100, marker='x', linewidths=1)
        print(trk[0], trk[1])
        axes[i, 0].set_xlim(0, map_size[0])
        axes[i, 0].set_ylim(0, map_size[1])
        axes[i, 0].set_xlabel('X label')
        axes[i, 0].set_ylabel('Y label')
        
        # 马氏距离可移动区域
        axes[i, 1].imshow(binary_map_m.T, cmap='Greens', alpha=0.5)
        axes[i, 1].set_title(f'pedestrian {i+1} - m_distance')
        axes[i, 1].scatter(trk[1], trk[0], color='red', s=100, marker='x', linewidths=1)
        axes[i, 1].set_xlim(0, map_size[0])
        axes[i, 1].set_ylim(0, map_size[1])
        axes[i, 1].set_xlabel('X label')
        axes[i, 1].set_ylabel('Y label')
    
    plt.tight_layout()
    
    # 保存图片
    output_path = os.path.join(output_dir, f'{file_prefix}_all_pedestrians.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"保存总体图：{output_path}")
    
    # 为每个行人单独保存图片
    for i, (trk, binary_map_e, binary_map_m) in enumerate(zip(trackers, binary_map_e_list, binary_map_m_list)):
        # 创建单独的图
        plt.figure(figsize=(12, 5))
        
        # 欧几里得距离可移动区域
        plt.subplot(1, 2, 1)
        plt.imshow(binary_map_e.T, cmap='Blues', alpha=0.5)
        plt.title(f'pedestrian {i+1} - e_distance')
        plt.scatter(trk[1], trk[0], color='red', s=100, marker='x', linewidths=1)
        plt.xlim(0, map_size[0])
        plt.ylim(0, map_size[1])
        plt.xlabel('X label')
        plt.ylabel('Y label')
        
        # 马氏距离可移动区域
        plt.subplot(1, 2, 2)
        plt.imshow(binary_map_m.T, cmap='Greens', alpha=0.5)
        plt.title(f'pedestrian {i+1} - m_distance')
        plt.scatter(trk[1], trk[0], color='red', s=100, marker='x', linewidths=1)
        plt.xlim(0, map_size[0])
        plt.ylim(0, map_size[1])
        plt.xlabel('X label')
        plt.ylabel('Y label')
        
        plt.tight_layout()
        
        # 单独保存每个行人的图片
        single_output_path = os.path.join(output_dir, f'{file_prefix}_pedestrian_{i+1}.png')
        plt.savefig(single_output_path, dpi=300, bbox_inches='tight')
        print(f"保存行人 {i+1} 的图：{single_output_path}")
        plt.close()
    
    plt.close('all')