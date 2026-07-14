import cv2
import numpy as np
import math

class ImpactedToothAnalyzer:
    def __init__(self):
        """
        Dental_009: Impacted Tooth Detailed Analysis Module
        매복치(3rd Molar)와 인접 제2대구치(2nd Molar)의 폴리곤 데이터를 바탕으로
        발치 난이도 및 Winter's Classification을 도출합니다.
        """
        pass

    def get_long_axis_vector(self, contour):
        """
        치아 폴리곤(Contour)으로부터 주축(Long Axis) 벡터와 중심점을 계산합니다.
        """
        if len(contour) < 3:
            return None, None
        
        pts = contour.reshape(-1, 2).astype(np.float64)
        mean, eigenvectors = cv2.PCACompute(pts, mean=None)
        
        center = mean[0]
        axis = eigenvectors[0]
        
        if axis[1] > 0:
            axis = -axis
            
        return center, axis

    def calculate_angle_diff(self, axis_target, axis_adjacent):
        """
        두 주축 벡터 간의 사잇각(도)을 계산합니다.
        """
        v1_u = axis_target / np.linalg.norm(axis_target)
        v2_u = axis_adjacent / np.linalg.norm(axis_adjacent)
        
        cross_prod = np.cross(v2_u, v1_u)
        dot_prod = np.dot(v1_u, v2_u)
        
        angle_rad = np.arctan2(cross_prod, dot_prod)
        angle_deg = np.degrees(angle_rad)
        
        return angle_deg

    def evaluate_winters_classification(self, angle, quadrant):
        """
        Winter's Classification 판별
        - Mesioangular (근심경사)
        - Distoangular (원심경사)
        - Vertical (수직)
        - Horizontal (수평)
        """
        abs_angle = abs(angle)
        
        if abs_angle <= 10:
            return "Vertical"
        elif 10 < abs_angle <= 75:
            if (quadrant in [3, 4] and angle > 0) or (quadrant in [1, 2] and angle < 0): 
                return "Mesioangular"
            else:
                return "Distoangular"
        elif 75 < abs_angle <= 105:
            return "Horizontal"
        else:
            return "Distoangular/Inverted"

    def evaluate_eruption_status(self, target_contour, adjacent_contour):
        """
        맹출 상태 평가
        - Fully Erupted (완전맹출)
        - Partially Erupted (부분맹출)
        - Fully Impacted (완전매복)
        """
        target_pts = target_contour.reshape(-1, 2)
        adj_pts = adjacent_contour.reshape(-1, 2)
        
        target_highest_y = np.min(target_pts[:, 1]) 
        adj_highest_y = np.min(adj_pts[:, 1])
        adj_lowest_y = np.max(adj_pts[:, 1])
        
        adj_cervical_y = adj_highest_y + (adj_lowest_y - adj_highest_y) * 0.5
        
        if target_highest_y <= adj_highest_y + 10:
            return "Fully Erupted"
        elif adj_highest_y + 10 < target_highest_y <= adj_cervical_y:
            return "Partially Erupted"
        else:
            return "Fully Impacted"

    def analyze_impacted_tooth(self, target_tooth_contour, target_fdi, adjacent_tooth_contour):
        _, t_axis = self.get_long_axis_vector(target_tooth_contour)
        _, a_axis = self.get_long_axis_vector(adjacent_tooth_contour)
        
        if t_axis is None or a_axis is None:
            return {"error": "Insufficient contour points."}
            
        angle = self.calculate_angle_diff(t_axis, a_axis)
        quadrant = int(str(target_fdi)[0]) if target_fdi else 3
        winters_class = self.evaluate_winters_classification(angle, quadrant)
        eruption_status = self.evaluate_eruption_status(target_tooth_contour, adjacent_tooth_contour)
        
        return {
            "fdi": target_fdi,
            "angle_diff": round(angle, 2),
            "winters_class": winters_class,
            "eruption_status": eruption_status
        }
