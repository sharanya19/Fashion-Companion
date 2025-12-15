"""
Celebrity Color Season Validation Dataset
Based on professional color analysis consensus
"""

CELEBRITY_DATASET = {
    # WINTER SUBTYPES
    "winter": {
        "true_winter": [
            {
                "name": "Anne Hathaway",
                "expected_season": "Winter",
                "expected_subtype": "True Winter",
                "characteristics": {
                    "skin": "Fair to medium, cool undertone",
                    "hair": "Dark brown to black",
                    "eyes": "Deep brown",
                    "contrast": "High (dark hair, light skin)",
                    "notes": "Classic True Winter - high contrast, cool undertone"
                }
            },
            {
                "name": "Megan Fox",
                "expected_season": "Winter",
                "expected_subtype": "True Winter",
                "characteristics": {
                    "skin": "Medium, cool undertone",
                    "hair": "Dark brown/black",
                    "eyes": "Blue-green",
                    "contrast": "High",
                    "notes": "Cool undertone with high contrast"
                }
            },
            {
                "name": "Katy Perry",
                "expected_season": "Winter",
                "expected_subtype": "Bright Winter",
                "characteristics": {
                    "skin": "Fair, cool undertone",
                    "hair": "Black (natural dark brown)",
                    "eyes": "Bright blue",
                    "contrast": "Very high",
                    "notes": "Bright, clear colors - Bright Winter"
                }
            }
        ],
        "deep_winter": [
            {
                "name": "Sandra Bullock",
                "expected_season": "Winter",
                "expected_subtype": "Deep Winter",
                "characteristics": {
                    "skin": "Medium-deep, neutral-cool",
                    "hair": "Dark brown",
                    "eyes": "Dark brown",
                    "contrast": "Moderate-high",
                    "notes": "Deeper coloring, still cool"
                }
            }
        ]
    },
    
    # SPRING SUBTYPES
    "spring": {
        "light_spring": [
            {
                "name": "Blake Lively",
                "expected_season": "Spring",
                "expected_subtype": "Light Spring",
                "characteristics": {
                    "skin": "Fair to light, warm undertone",
                    "hair": "Blonde (natural or highlighted)",
                    "eyes": "Light (blue/green/hazel)",
                    "contrast": "Low to moderate",
                    "notes": "Light, warm, delicate coloring"
                }
            },
            {
                "name": "Scarlett Johansson",
                "expected_season": "Spring",
                "expected_subtype": "Light Spring",
                "characteristics": {
                    "skin": "Fair, warm undertone",
                    "hair": "Blonde",
                    "eyes": "Green",
                    "contrast": "Low-moderate",
                    "notes": "Warm, light coloring"
                }
            }
        ],
        "true_spring": [
            {
                "name": "Emma Stone",
                "expected_season": "Spring",
                "expected_subtype": "True Spring",
                "characteristics": {
                    "skin": "Fair, warm undertone",
                    "hair": "Auburn/red (natural)",
                    "eyes": "Green",
                    "contrast": "Moderate",
                    "notes": "Warm, clear, bright - classic Spring"
                }
            }
        ],
        "bright_spring": [
            {
                "name": "Beyoncé",
                "expected_season": "Spring",
                "expected_subtype": "Bright Spring",
                "characteristics": {
                    "skin": "Medium, warm undertone",
                    "hair": "Dark brown (natural)",
                    "eyes": "Dark brown",
                    "contrast": "High",
                    "notes": "Warm undertone with high contrast and brightness"
                }
            }
        ]
    },
    
    # SUMMER SUBTYPES
    "summer": {
        "light_summer": [
            {
                "name": "Gwyneth Paltrow",
                "expected_season": "Summer",
                "expected_subtype": "Light Summer",
                "characteristics": {
                    "skin": "Fair, cool undertone",
                    "hair": "Blonde (ash/cool tones)",
                    "eyes": "Blue",
                    "contrast": "Low",
                    "notes": "Cool, light, muted coloring"
                }
            }
        ],
        "true_summer": [
            {
                "name": "Emily Blunt",
                "expected_season": "Summer",
                "expected_subtype": "True Summer",
                "characteristics": {
                    "skin": "Fair to medium, cool undertone",
                    "hair": "Ash blonde to light brown",
                    "eyes": "Blue/gray",
                    "contrast": "Low-moderate",
                    "notes": "Cool, soft, muted"
                }
            }
        ],
        "soft_summer": [
            {
                "name": "Sarah Jessica Parker",
                "expected_season": "Summer",
                "expected_subtype": "Soft Summer",
                "characteristics": {
                    "skin": "Medium, neutral-cool",
                    "hair": "Light brown (ash tones)",
                    "eyes": "Blue/gray",
                    "contrast": "Low",
                    "notes": "Muted, soft coloring"
                }
            }
        ]
    },
    
    # AUTUMN SUBTYPES
    "autumn": {
        "true_autumn": [
            {
                "name": "Julia Roberts",
                "expected_season": "Autumn",
                "expected_subtype": "True Autumn",
                "characteristics": {
                    "skin": "Medium, warm undertone",
                    "hair": "Auburn/red-brown",
                    "eyes": "Brown/hazel",
                    "contrast": "Moderate",
                    "notes": "Warm, rich, earthy"
                }
            },
            {
                "name": "Jessica Chastain",
                "expected_season": "Autumn",
                "expected_subtype": "True Autumn",
                "characteristics": {
                    "skin": "Fair, warm undertone",
                    "hair": "Red/auburn",
                    "eyes": "Green/hazel",
                    "contrast": "Moderate",
                    "notes": "Classic Autumn - warm, rich"
                }
            }
        ],
        "soft_autumn": [
            {
                "name": "Drew Barrymore",
                "expected_season": "Autumn",
                "expected_subtype": "Soft Autumn",
                "characteristics": {
                    "skin": "Fair to medium, warm",
                    "hair": "Blonde to light brown (warm)",
                    "eyes": "Green/hazel",
                    "contrast": "Low-moderate",
                    "notes": "Soft, muted, warm"
                }
            }
        ],
        "deep_autumn": [
            {
                "name": "Kim Kardashian",
                "expected_season": "Autumn",
                "expected_subtype": "Deep Autumn",
                "characteristics": {
                    "skin": "Medium-deep, warm undertone",
                    "hair": "Dark brown/black",
                    "eyes": "Dark brown",
                    "contrast": "Moderate-high",
                    "notes": "Deep, warm coloring"
                }
            },
            {
                "name": "Mindy Kaling",
                "expected_season": "Autumn",
                "expected_subtype": "Deep Autumn",
                "characteristics": {
                    "skin": "Deep, warm undertone",
                    "hair": "Dark brown/black",
                    "eyes": "Dark brown",
                    "contrast": "Low-moderate",
                    "notes": "Deep, warm, rich"
                }
            }
        ]
    }
}

def get_all_test_cases():
    """Flatten dataset into list of test cases"""
    test_cases = []
    for season_group in CELEBRITY_DATASET.values():
        for subtype_group in season_group.values():
            test_cases.extend(subtype_group)
    return test_cases

def get_test_case_by_name(name: str):
    """Find test case by celebrity name"""
    for test_case in get_all_test_cases():
        if test_case['name'].lower() == name.lower():
            return test_case
    return None

# Summary statistics
def get_dataset_stats():
    """Get dataset statistics"""
    all_cases = get_all_test_cases()
    
    season_counts = {}
    subtype_counts = {}
    
    for case in all_cases:
        season = case['expected_season']
        subtype = case['expected_subtype']
        
        season_counts[season] = season_counts.get(season, 0) + 1
        subtype_counts[subtype] = subtype_counts.get(subtype, 0) + 1
    
    return {
        'total_cases': len(all_cases),
        'season_distribution': season_counts,
        'subtype_distribution': subtype_counts
    }
