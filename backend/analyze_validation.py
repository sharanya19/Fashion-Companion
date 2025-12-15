"""
Validation Results Analysis
"""
import json

# Load results
with open('validation_results.json', 'r') as f:
    results = json.load(f)

print("="*80)
print("📊 CELEBRITY COLOR SEASON VALIDATION RESULTS")
print("="*80)

# Calculate metrics
total = len(results)
season_correct = sum(1 for r in results if r['season_match'])
subtype_correct = sum(1 for r in results if r['subtype_match'])

season_accuracy = (season_correct / total) * 100
subtype_accuracy = (subtype_correct / total) * 100

print(f"\n✅ ACCURACY METRICS:")
print(f"   Total Tests: {total}")
print(f"   Season Accuracy: {season_correct}/{total} ({season_accuracy:.1f}%)")
print(f"   Subtype Accuracy: {subtype_correct}/{total} ({subtype_accuracy:.1f}%)")

# Breakdown by season
print(f"\n📈 BREAKDOWN BY SEASON:")
seasons = {}
for r in results:
    expected_season = r['expected'].split(' - ')[0]
    if expected_season not in seasons:
        seasons[expected_season] = {'total': 0, 'correct': 0}
    seasons[expected_season]['total'] += 1
    if r['season_match']:
        seasons[expected_season]['correct'] += 1

for season, stats in sorted(seasons.items()):
    acc = (stats['correct'] / stats['total']) * 100
    print(f"   {season}: {stats['correct']}/{stats['total']} ({acc:.0f}%)")

# Show all results
print(f"\n📋 DETAILED RESULTS:")
print("-"*80)
for i, r in enumerate(results, 1):
    status = "✅" if r['subtype_match'] else ("⚠️ " if r['season_match'] else "❌")
    print(f"{i:2d}. {status} {r['name']:25s} | Expected: {r['expected']:30s} | Got: {r['actual']}")

# Show mismatches
mismatches = [r for r in results if not r['subtype_match']]
print(f"\n❌ SUBTYPE MISMATCHES ({len(mismatches)}):")
print("-"*80)
for m in mismatches:
    print(f"   • {m['name']:25s}: {m['expected']:30s} → {m['actual']}")
    
# Analysis of issues
print(f"\n🔍 ISSUE ANALYSIS:")
print("-"*80)

# Issue 1: True Winter vs Bright Winter confusion
true_winter_issues = [m for m in mismatches if 'True Winter' in m['expected'] and 'Bright Winter' in m['actual']]
if true_winter_issues:
    print(f"\n1. True Winter → Bright Winter ({len(true_winter_issues)} cases)")
    print(f"   Affected: {', '.join([m['name'] for m in true_winter_issues])}")
    print(f"   Likely cause: Chroma threshold too low for True Winter")
    print(f"   Fix: Adjust Bright Winter chroma gate or True Winter chroma range")

# Issue 2: True Spring misclassification
true_spring_issues = [m for m in mismatches if 'True Spring' in m['expected'] and m['expected'] != m['actual']]
if true_spring_issues:
    print(f"\n2. True Spring Misclassification ({len(true_spring_issues)} cases)")
    for m in true_spring_issues:
        print(f"   • {m['name']}: {m['expected']} → {m['actual']}")
    print(f"   Likely cause: Skin lightness or chroma thresholds")

# Issue 3: Deep Autumn detection
deep_autumn_issues = [m for m in mismatches if 'Deep Autumn' in m['expected']]
if deep_autumn_issues:
    print(f"\n3. Deep Autumn → True Autumn ({len(deep_autumn_issues)} cases)")
    print(f"   Affected: {', '.join([m['name'] for m in deep_autumn_issues])}")
    print(f"   Likely cause: Skin L threshold for Deep Autumn too strict (>55)")
    print(f"   Fix: Relax Deep Autumn skin_l gate from 55 to 60")

# Issue 4: Jessica Chastain (Autumn → Spring)
jessica_issue = [m for m in mismatches if m['name'] == 'Jessica Chastain']
if jessica_issue:
    print(f"\n4. Jessica Chastain: Autumn → Spring")
    print(f"   This is a SEASON-level error (most serious)")
    print(f"   Likely cause: Fair skin + red hair being read as Light Spring")
    print(f"   Fix: Add True Autumn protection for red/auburn hair")

# Grade
print(f"\n📈 OVERALL GRADE:")
if subtype_accuracy >= 85:
    grade = "A (Excellent)"
    recommendation = "System is production-ready"
elif subtype_accuracy >= 75:
    grade = "B (Good)"
    recommendation = "Minor tweaks recommended before launch"
elif subtype_accuracy >= 65:
    grade = "C (Fair)"
    recommendation = "Significant improvements needed"
else:
    grade = "D (Needs Work)"
    recommendation = "Major overhaul required"

print(f"   Grade: {grade}")
print(f"   Subtype Accuracy: {subtype_accuracy:.1f}%")
print(f"   Season Accuracy: {season_accuracy:.1f}%")
print(f"   Recommendation: {recommendation}")

print("\n" + "="*80)
