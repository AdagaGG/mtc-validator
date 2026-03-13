"""
Normas de tolerancias para elementos metalúrgicos según estándares ASTM/SAE
"""

NORMAS = {
    "SAE1020": {
        "C_%": {"min": 0.18, "max": 0.23},
        "Mn_%": {"min": 0.30, "max": 0.55},
        "P_%": {"min": 0.0, "max": 0.04},
        "S_%": {"min": 0.0, "max": 0.05},
        "YS_MPa": {"min": 295, "max": 380},
        "UTS_MPa": {"min": 435, "max": 565},
        "Elong_%": {"min": 25, "max": 100},
    },
    "SAE1045": {
        "C_%": {"min": 0.43, "max": 0.50},
        "Mn_%": {"min": 0.60, "max": 0.90},
        "P_%": {"min": 0.0, "max": 0.04},
        "S_%": {"min": 0.0, "max": 0.05},
        "YS_MPa": {"min": 310, "max": 400},
        "UTS_MPa": {"min": 570, "max": 700},
        "Elong_%": {"min": 16, "max": 100},
    },
    "ASTM_A36": {
        "C_%": {"min": 0.0, "max": 0.26},
        "Mn_%": {"min": 0.0, "max": 1.03},
        "P_%": {"min": 0.0, "max": 0.04},
        "S_%": {"min": 0.0, "max": 0.05},
        "YS_MPa": {"min": 250, "max": 400},
        "UTS_MPa": {"min": 400, "max": 550},
        "Elong_%": {"min": 20, "max": 100},
    },
    "AISI4140": {
        "C_%": {"min": 0.38, "max": 0.43},
        "Mn_%": {"min": 0.75, "max": 1.00},
        "P_%": {"min": 0.0, "max": 0.035},
        "S_%": {"min": 0.0, "max": 0.040},
        "YS_MPa": {"min": 415, "max": 550},
        "UTS_MPa": {"min": 655, "max": 860},
        "Elong_%": {"min": 16, "max": 100},
    },
}
