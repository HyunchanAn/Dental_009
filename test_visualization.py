import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.analyzer import ImpactedToothAnalyzer

def create_dummy_contour(center_x, center_y, width, height, angle_deg):
    """지정된 중심, 너비, 높이, 회전각도를 가진 가상의 직사각형 폴리곤(치아 대체) 생성"""
    rect = ((center_x, center_y), (width, height), angle_deg)
    box = cv2.boxPoints(rect)
    return np.int32(box)

def test_winters_classification_visualization():
    analyzer = ImpactedToothAnalyzer()
    
    # 가상의 이미지 캔버스 생성 (500x500)
    img = np.zeros((500, 500, 3), dtype=np.uint8)
    
    # 37번 인접치 (제2대구치) - 수직에 가깝게 서 있음
    a_center = (250, 350)
    a_contour = create_dummy_contour(a_center[0], a_center[1], 40, 100, 0) # 수직
    
    # 38번 매복치 (근심경사 - Mesioangular 예시)
    t_center = (150, 380) # 37번보다 살짝 아래, 왼쪽에 위치 (하악 좌측)
    t_contour = create_dummy_contour(t_center[0], t_center[1], 40, 100, -45) # 45도 기울어짐
    
    # 폴리곤 그리기
    cv2.drawContours(img, [a_contour], 0, (0, 255, 0), 2)
    cv2.drawContours(img, [t_contour], 0, (0, 0, 255), 2)
    
    # 분석
    res = analyzer.analyze_impacted_tooth(t_contour, 38, a_contour)
    
    # 장축 축 그리기 (37번)
    a_c, a_vec = analyzer.get_long_axis_vector(a_contour)
    a_end = (int(a_c[0] + a_vec[0]*100), int(a_c[1] + a_vec[1]*100))
    cv2.line(img, (int(a_c[0]), int(a_c[1])), a_end, (0, 255, 0), 2)
    
    # 장축 축 그리기 (38번)
    t_c, t_vec = analyzer.get_long_axis_vector(t_contour)
    t_end = (int(t_c[0] + t_vec[0]*100), int(t_c[1] + t_vec[1]*100))
    cv2.line(img, (int(t_c[0]), int(t_c[1])), t_end, (0, 0, 255), 2)
    
    # 텍스트 출력
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, f"FDI: {res['fdi']}", (10, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Angle: {res['angle_diff']} deg", (10, 60), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Class: {res['winters_class']}", (10, 90), font, 0.7, (255, 255, 255), 2)
    cv2.putText(img, f"Depth: {res['eruption_status']}", (10, 120), font, 0.7, (255, 255, 255), 2)
    
    cv2.imwrite("test_visualization.jpg", img)
    print("test_visualization.jpg generated successfully.")

if __name__ == "__main__":
    test_winters_classification_visualization()
