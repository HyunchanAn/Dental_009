import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analyzer import ImpactedToothAnalyzer


def create_dummy_contour(center_x, center_y, width, height, angle_deg):
    rect = ((center_x, center_y), (width, height), angle_deg)
    box = cv2.boxPoints(rect)
    return np.int32(box)


def run_winters_classification_visualization():
    analyzer = ImpactedToothAnalyzer()
    img = np.zeros((500, 500, 3), dtype=np.uint8)

    a_center = (250, 350)
    a_contour = create_dummy_contour(a_center[0], a_center[1], 40, 100, 0)

    t_center = (150, 380)
    t_contour = create_dummy_contour(t_center[0], t_center[1], 40, 100, -45)

    cv2.drawContours(img, [a_contour], 0, (0, 255, 0), 2)
    cv2.drawContours(img, [t_contour], 0, (0, 0, 255), 2)

    res = analyzer.analyze_impacted_tooth(t_contour, 38, a_contour)

    a_c, a_vec = analyzer.get_long_axis_vector(a_contour)
    a_end = (int(a_c[0] + a_vec[0] * 100), int(a_c[1] + a_vec[1] * 100))
    cv2.line(img, (int(a_c[0]), int(a_c[1])), a_end, (0, 255, 0), 2)

    t_c, t_vec = analyzer.get_long_axis_vector(t_contour)
    t_end = (int(t_c[0] + t_vec[0] * 100), int(t_c[1] + t_vec[1] * 100))
    cv2.line(img, (int(t_c[0]), int(t_c[1])), t_end, (0, 0, 255), 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, f"FDI: {res['fdi']}", (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Angle: {res['angle_diff']} deg", (10, 60), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Class: {res['winters_class']}", (10, 90), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Depth: {res['eruption_status']}", (10, 120), font, 0.7, (255, 255, 255), 2)

    cv2.imwrite("test_visualization.jpg", img)
    print("test_visualization.jpg generated successfully.")


if __name__ == "__main__":
    run_winters_classification_visualization()
