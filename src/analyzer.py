import cv2
import numpy as np
import math


class ImpactedToothAnalyzer:
    def __init__(self):
        """
        Dental_009: Impacted Tooth Detailed Analysis Module
        Analyzes third-molar (FDI #18, #28, #38, #48) and adjacent second-molar
        (#17, #27, #37, #47) polygon contours using PCA long-axis estimation,
        Winter's angular classification (1926), and Pell & Gregory occlusal depth
        levels (1933).
        """
        pass

    def get_long_axis_vector(self, contour):
        """
        Computes the principal long-axis unit vector (pointing toward the crown/occlusal
        direction, y <= 0) and centroid from a 2D tooth contour using PCA.
        """
        if contour is None or len(contour) < 3:
            return None, None

        pts = np.asarray(contour).reshape(-1, 2).astype(np.float64)
        mean, eigenvectors = cv2.PCACompute(pts, mean=None)

        center = mean[0]
        axis = eigenvectors[0]

        if axis[1] > 0:
            axis = -axis

        return center, axis

    def calculate_angle_diff(self, axis_target, axis_adjacent):
        """
        Computes the signed angle (degrees) between the target third-molar long axis
        and the adjacent second-molar long axis.
        """
        v1_u = axis_target / np.linalg.norm(axis_target)
        v2_u = axis_adjacent / np.linalg.norm(axis_adjacent)

        cross_prod = float(v2_u[0] * v1_u[1] - v2_u[1] * v1_u[0])
        dot_prod = float(np.dot(v1_u, v2_u))

        angle_rad = np.arctan2(cross_prod, dot_prod)
        angle_deg = np.degrees(angle_rad)

        return float(angle_deg)

    def evaluate_winters_classification(self, angle, quadrant):
        """
        Winter's Classification (Winter, 1926; Quek et al., Int J Oral Maxillofac Surg 2003):
        - Vertical: |angle| <= 10 deg
        - Mesioangular / Distoangular: 10 deg < |angle| <= 75 deg (sign depends on quadrant)
        - Horizontal: 75 deg < |angle| <= 105 deg
        - Distoangular/Inverted: |angle| > 105 deg
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

    def evaluate_eruption_status(self, target_contour, adjacent_contour, quadrant=3):
        """
        Evaluates vertical eruption depth (Pell & Gregory Level A/B/C proxy):
        - Fully Erupted (Level A): occlusal plane within 10 px of adjacent 2nd molar
        - Partially Erupted (Level B): occlusal point between occlusal plane and cervical line,
          or exploratory bounding-box height ratio heuristic (target_h < 0.88 * adj_h)
        - Fully Impacted (Level C): occlusal point apical to the adjacent cervical midpoint

        Note: The 88% height ratio (target_h < adj_h * 0.88) is an exploratory engineering
        heuristic to catch partially erupted or foreshortened third-molar masks in 2D
        panoramic projections, not a standalone clinical standard.
        """
        target_pts = np.asarray(target_contour).reshape(-1, 2)
        adj_pts = np.asarray(adjacent_contour).reshape(-1, 2)

        target_h = float(np.max(target_pts[:, 1]) - np.min(target_pts[:, 1]))
        adj_h = float(np.max(adj_pts[:, 1]) - np.min(adj_pts[:, 1]))

        if quadrant in [1, 2]:  # Maxilla: occlusal surface has larger y (inferior)
            target_occlusal_y = float(np.max(target_pts[:, 1]))
            adj_occlusal_y = float(np.max(adj_pts[:, 1]))
            adj_apex_y = float(np.min(adj_pts[:, 1]))
            adj_cervical_y = adj_occlusal_y - (adj_occlusal_y - adj_apex_y) * 0.5

            if target_occlusal_y < adj_cervical_y:
                return "Fully Impacted"
            if adj_h > 20 and target_h < adj_h * 0.88:
                return "Partially Erupted"
            if target_occlusal_y >= adj_occlusal_y - 10:
                return "Fully Erupted"
            return "Partially Erupted"
        else:  # Mandible: occlusal surface has smaller y (superior)
            target_occlusal_y = float(np.min(target_pts[:, 1]))
            adj_occlusal_y = float(np.min(adj_pts[:, 1]))
            adj_apex_y = float(np.max(adj_pts[:, 1]))
            adj_cervical_y = adj_occlusal_y + (adj_apex_y - adj_occlusal_y) * 0.5

            if target_occlusal_y > adj_cervical_y:
                return "Fully Impacted"
            if adj_h > 20 and target_h < adj_h * 0.88:
                return "Partially Erupted"
            if target_occlusal_y <= adj_occlusal_y + 10:
                return "Fully Erupted"
            return "Partially Erupted"

    @staticmethod
    def evaluate_pell_gregory_level(eruption_status: str) -> str:
        mapping = {
            "Fully Erupted": "Level A",
            "Partially Erupted": "Level B",
            "Fully Impacted": "Level C",
        }
        return mapping.get(eruption_status, "Unknown")

    def analyze_impacted_tooth(self, target_tooth_contour, target_fdi, adjacent_tooth_contour):
        _, t_axis = self.get_long_axis_vector(target_tooth_contour)
        _, a_axis = self.get_long_axis_vector(adjacent_tooth_contour)

        if t_axis is None or a_axis is None:
            return {"error": "Insufficient contour points."}

        angle = self.calculate_angle_diff(t_axis, a_axis)
        quadrant = int(str(target_fdi).lstrip("#")[0]) if target_fdi else 3
        winters_class = self.evaluate_winters_classification(angle, quadrant)
        eruption_status = self.evaluate_eruption_status(
            target_tooth_contour, adjacent_tooth_contour, quadrant=quadrant
        )
        pell_gregory_level = self.evaluate_pell_gregory_level(eruption_status)

        return {
            "fdi": target_fdi,
            "angle_diff": round(angle, 2),
            "winters_class": winters_class,
            "eruption_status": eruption_status,
            "pell_gregory_level": pell_gregory_level,
        }


ImpactionAnalyzer = ImpactedToothAnalyzer
