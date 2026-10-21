import os
import sys
import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analyzer import ImpactedToothAnalyzer, ImpactionAnalyzer


def make_rotated_rect_contour(cx: float, cy: float, width: float, height: float, angle_deg: float) -> np.ndarray:
    rect = ((float(cx), float(cy)), (float(width), float(height)), float(angle_deg))
    box = cv2.boxPoints(rect)
    return np.int32(box)


def bbox_to_contour(bbox):
    x1, y1, x2, y2 = bbox
    return np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.int32)


def compute_iou(box_a, box_b) -> float:
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])
    inter = max(0.0, x_b - x_a) * max(0.0, y_b - y_a)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    return inter / (area_a + area_b - inter + 1e-9)


def test_winters_angular_categories():
    analyzer = ImpactionAnalyzer()
    assert analyzer.evaluate_winters_classification(0.0, quadrant=3) == "Vertical"
    assert analyzer.evaluate_winters_classification(8.5, quadrant=4) == "Vertical"
    assert analyzer.evaluate_winters_classification(35.0, quadrant=3) == "Mesioangular"
    assert analyzer.evaluate_winters_classification(-35.0, quadrant=3) == "Distoangular"
    assert analyzer.evaluate_winters_classification(-35.0, quadrant=1) == "Mesioangular"
    assert analyzer.evaluate_winters_classification(35.0, quadrant=2) == "Distoangular"
    assert analyzer.evaluate_winters_classification(88.0, quadrant=3) == "Horizontal"
    assert analyzer.evaluate_winters_classification(120.0, quadrant=4) == "Distoangular/Inverted"


def test_pell_gregory_depth_levels_and_88_percent_heuristic():
    analyzer = ImpactedToothAnalyzer()
    # Adjacent lower 2nd molar (#37): y from 300 (occlusal) to 400 (apex), height = 100
    adj_37 = bbox_to_contour([200, 300, 240, 400])

    # Level A (Fully Erupted): y from 302 to 402 (height 100 >= 88, occlusal within 10px)
    target_level_a = bbox_to_contour([250, 302, 290, 402])
    res_a = analyzer.analyze_impacted_tooth(target_level_a, 38, adj_37)
    assert res_a["eruption_status"] == "Fully Erupted"
    assert res_a["pell_gregory_level"] == "Level A"

    # Level B via 88% height-ratio heuristic: y from 302 to 380 (height 78 < 88)
    target_heuristic_b = bbox_to_contour([250, 302, 290, 380])
    res_b_heur = analyzer.analyze_impacted_tooth(target_heuristic_b, 38, adj_37)
    assert res_b_heur["eruption_status"] == "Partially Erupted"
    assert res_b_heur["pell_gregory_level"] == "Level B"

    # Level B via occlusal depth between occlusal+10 (310) and cervical (350): y from 330 to 430
    target_level_b = bbox_to_contour([250, 330, 290, 430])
    res_b = analyzer.analyze_impacted_tooth(target_level_b, 38, adj_37)
    assert res_b["eruption_status"] == "Partially Erupted"
    assert res_b["pell_gregory_level"] == "Level B"

    # Level C (Fully Impacted): occlusal point > cervical midpoint (350), e.g., y from 365 to 455
    target_level_c = bbox_to_contour([250, 365, 290, 455])
    res_c = analyzer.analyze_impacted_tooth(target_level_c, 38, adj_37)
    assert res_c["eruption_status"] == "Fully Impacted"
    assert res_c["pell_gregory_level"] == "Level C"


def test_thegem_gold_four_third_molars_verification():
    """
    Verifies the 4 ground-truth impacted third molars (#18, #28, #38, #48)
    from the TheGem panoramic benchmark (panoramic-x-ray-thegem-blog-default.jpg).
    """
    gold_vs_pred = [
        {
            "fdi": 18,
            "gold_bbox": [185.0, 111.0, 251.0, 170.0],
            "pred_bbox": [195.7, 130.9, 266.3, 212.7],
            "adj_bbox": [230.0, 150.0, 285.0, 260.0],
            "expected_iou": 0.288,
        },
        {
            "fdi": 28,
            "gold_bbox": [907.0, 100.0, 982.0, 163.0],
            "pred_bbox": [905.5, 98.9, 978.3, 201.6],
            "adj_bbox": [850.0, 145.0, 905.0, 255.0],
            "expected_iou": 0.583,
        },
        {
            "fdi": 38,
            "gold_bbox": [925.0, 285.0, 1024.0, 390.0],
            "pred_bbox": [920.6, 274.7, 1039.5, 426.1],
            "adj_bbox": [845.0, 265.0, 915.0, 395.0],
            "expected_iou": 0.577,
        },
        {
            "fdi": 48,
            "gold_bbox": [123.0, 315.0, 224.0, 408.0],
            "pred_bbox": [96.0, 306.9, 227.1, 421.8],
            "adj_bbox": [230.0, 275.0, 300.0, 405.0],
            "expected_iou": 0.624,
        },
    ]

    analyzer = ImpactionAnalyzer()
    for item in gold_vs_pred:
        iou = compute_iou(item["gold_bbox"], item["pred_bbox"])
        assert iou >= 0.25
        assert iou == pytest.approx(item["expected_iou"], abs=0.01)

        t_contour = bbox_to_contour(item["pred_bbox"])
        a_contour = bbox_to_contour(item["adj_bbox"])
        res = analyzer.analyze_impacted_tooth(t_contour, item["fdi"], a_contour)
        assert "error" not in res
        assert res["fdi"] == item["fdi"]
        assert res["winters_class"] in {
            "Vertical",
            "Mesioangular",
            "Distoangular",
            "Horizontal",
            "Distoangular/Inverted",
        }
        assert res["eruption_status"] in {"Fully Erupted", "Partially Erupted", "Fully Impacted"}
        assert res["pell_gregory_level"] in {"Level A", "Level B", "Level C"}
