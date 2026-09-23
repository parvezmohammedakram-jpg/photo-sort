# PhotoSort -- Scoring Engine Specification

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Purpose

The scoring engine combines analysis results from all five modules into a single quality score between 0 and 100. The score drives automatic categorization and provides a consistent, objective ranking mechanism for comparing photographs.

---

## 2. Design Principles

1. **Deterministic.** Same analysis inputs always produce the same score.
2. **Explainable.** Every component of the score can be traced back to a specific metric.
3. **Configurable.** Weights and thresholds are externalized, not hard-coded.
4. **Testable.** The scoring function can be unit-tested with synthetic inputs.
5. **Transparent.** No hidden factors or random values.

---

## 3. Scoring Components

### 3.1 Sharpness Score (0-100)

**Source:** BlurAnalyzer sharpness_score (Laplacian variance)

**Normalization:**

```
if raw >= SHARP_THRESHOLD:
    normalized = 100

elif raw >= BORDERLINE_THRESHOLD:
    # Linear interpolation between borderline (50) and sharp (100)
    range = SHARP_THRESHOLD - BORDERLINE_THRESHOLD
    position = (raw - BORDERLINE_THRESHOLD) / range
    normalized = 50 + (position * 50)

else:
    # Linear interpolation between 0 and borderline (50)
    position = raw / BORDERLINE_THRESHOLD
    normalized = position * 50
```

**Result:** A value from 0 (completely blurry) to 100 (sharp).

---

### 3.2 Resolution Score (0-100)

**Source:** ResolutionAnalyzer megapixels

**Normalization:**

```
TARGET_MEGAPIXELS = 8.0  # Reference point for "good" resolution

if megapixels >= TARGET_MEGAPIXELS:
    normalized = 100

elif megapixels >= MIN_MEGAPIXELS:
    range = TARGET_MEGAPIXELS - MIN_MEGAPIXELS
    position = (megapixels - MIN_MEGAPIXELS) / range
    normalized = position * 100

else:
    normalized = 0
```

**Reasoning:** Resolution beyond 8 MP does not meaningfully improve photo usability for most purposes. Below minimum is penalized linearly.

---

### 3.3 Exposure Score (0-100)

**Source:** ExposureAnalyzer brightness_avg, dark_pixel_pct, bright_pixel_pct

**Normalization:**

```
# Ideal brightness range: 80-180 (center of histogram)
IDEAL_LOW = 80
IDEAL_HIGH = 180
IDEAL_CENTER = 130

if IDEAL_LOW <= brightness_avg <= IDEAL_HIGH:
    # Within ideal range
    distance_from_center = abs(brightness_avg - IDEAL_CENTER)
    max_distance = IDEAL_CENTER - IDEAL_LOW  # = 50
    brightness_component = 100 - (distance_from_center / max_distance * 20)
else:
    # Outside ideal range
    if brightness_avg < IDEAL_LOW:
        distance = IDEAL_LOW - brightness_avg
        brightness_component = max(0, 80 - (distance / IDEAL_LOW * 80))
    else:
        distance = brightness_avg - IDEAL_HIGH
        max_over = 255 - IDEAL_HIGH  # = 75
        brightness_component = max(0, 80 - (distance / max_over * 80))

# Pixel distribution penalty
pixel_penalty = 0
if dark_pixel_pct > 30:
    pixel_penalty += (dark_pixel_pct - 30) * 0.5
if bright_pixel_pct > 30:
    pixel_penalty += (bright_pixel_pct - 30) * 0.5

normalized = max(0, min(100, brightness_component - pixel_penalty))
```

---

### 3.4 Face Score (0-100)

**Source:** FaceAnalyzer face_count, closed_eye_detected, face_status

**Normalization:**

This component is conditional. If no faces are expected/found, it should not penalize.

```
if face_status == "no_face":
    # No face is neutral, not a penalty
    normalized = 80  # Slightly below perfect but acceptable

elif face_status == "faces_detected" and not closed_eye_detected:
    # Faces found, eyes open = good
    normalized = 100

elif face_status == "closed_eyes_detected":
    # Closed eyes detected = significant penalty
    normalized = 30

elif face_status == "analysis_failed":
    # Analysis failure = neutral (don't penalize for technical issues)
    normalized = 70

else:
    normalized = 70
```

**Design note:** Images without faces (landscapes, objects, food) should not be penalized. The "no_face" score of 80 reflects this neutrality while acknowledging that the face module contributed no positive quality signal.

---

### 3.5 Duplicate Penalty

**Source:** DuplicateAnalyzer duplicate_group_id

```
if image is in a duplicate group:
    duplicate_penalty = 10  # Flat score reduction

else:
    duplicate_penalty = 0
```

Duplicates are not inherently "bad quality" -- they are organizational issues. The penalty is small: enough to differentiate duplicates but not enough to push a good photo into "poor" category.

---

## 4. Weight Configuration

| Component | Weight | Default |
|-----------|--------|---------|
| Sharpness | WEIGHT_SHARPNESS | 0.35 |
| Resolution | WEIGHT_RESOLUTION | 0.10 |
| Exposure | WEIGHT_EXPOSURE | 0.30 |
| Face/Eye | WEIGHT_FACE | 0.25 |

Weights sum to 1.0.

**Rationale:**
- **Sharpness (35%):** Blur is the most common and obvious quality defect. A blurry photo is almost never usable.
- **Exposure (30%):** Exposure problems are the second most impactful. Underexposed photos lose detail; overexposed photos clip highlights.
- **Face/Eye (25%):** For portrait and event photography, closed eyes can ruin an otherwise perfect shot.
- **Resolution (10%):** Resolution is rarely the deciding factor. Most modern cameras produce sufficient resolution. Low weight prevents it from dominating the score.

---

## 5. Final Score Calculation

```python
def calculate_quality_score(
    sharpness_normalized: float,
    resolution_normalized: float,
    exposure_normalized: float,
    face_normalized: float,
    is_duplicate: bool,
    weights: dict
) -> float:
    """
    Calculate final quality score.
    
    All normalized inputs are 0-100.
    Returns a score 0-100.
    """
    weighted_score = (
        sharpness_normalized * weights["sharpness"]
        + resolution_normalized * weights["resolution"]
        + exposure_normalized * weights["exposure"]
        + face_normalized * weights["face"]
    )
    
    # Apply duplicate penalty
    if is_duplicate:
        weighted_score = max(0, weighted_score - DUPLICATE_PENALTY)
    
    # Clamp to 0-100
    return round(max(0.0, min(100.0, weighted_score)), 1)
```

---

## 6. Category Classification

| Category | Condition |
|----------|-----------|
| Good / Select | quality_score >= GOOD_THRESHOLD |
| Review | quality_score >= REVIEW_THRESHOLD AND quality_score < GOOD_THRESHOLD |
| Poor Quality | quality_score < REVIEW_THRESHOLD |

**Default Thresholds:**

| Threshold | Default Value |
|-----------|--------------|
| GOOD_THRESHOLD | 70.0 |
| REVIEW_THRESHOLD | 40.0 |

---

## 7. Score Breakdown Example

### Example: Good Photo

```
Sharpness raw: 450 -> normalized: 100 -> weighted: 35.0
Resolution: 12.1 MP -> normalized: 100 -> weighted: 10.0
Brightness: 125 -> normalized: 96 -> weighted: 28.8
Face: 2 faces, eyes open -> normalized: 100 -> weighted: 25.0
Duplicate: No -> penalty: 0

Quality Score = 35.0 + 10.0 + 28.8 + 25.0 - 0 = 98.8
Category: Good
```

### Example: Review Photo

```
Sharpness raw: 65 -> normalized: 65 -> weighted: 22.75
Resolution: 3.2 MP -> normalized: 31.4 -> weighted: 3.14
Brightness: 68 -> normalized: 72 -> weighted: 21.6
Face: 1 face, closed eyes -> normalized: 30 -> weighted: 7.5
Duplicate: No -> penalty: 0

Quality Score = 22.75 + 3.14 + 21.6 + 7.5 = 54.99 -> 55.0
Category: Review
```

### Example: Poor Photo

```
Sharpness raw: 15 -> normalized: 15 -> weighted: 5.25
Resolution: 0.5 MP -> normalized: 0 -> weighted: 0
Brightness: 32 -> normalized: 18 -> weighted: 5.4
Face: analysis failed -> normalized: 70 -> weighted: 17.5
Duplicate: Yes -> penalty: 10

Quality Score = 5.25 + 0 + 5.4 + 17.5 - 10 = 18.15 -> 18.2
Category: Poor
```

---

## 8. Configuration Summary

All scoring parameters are centralized in `config.py`:

```python
# Scoring weights (must sum to 1.0)
WEIGHT_SHARPNESS = 0.35
WEIGHT_RESOLUTION = 0.10
WEIGHT_EXPOSURE = 0.30
WEIGHT_FACE = 0.25

# Category thresholds
GOOD_THRESHOLD = 70.0
REVIEW_THRESHOLD = 40.0

# Duplicate penalty
DUPLICATE_PENALTY = 10.0

# Resolution reference
TARGET_MEGAPIXELS = 8.0

# Exposure ideal range
EXPOSURE_IDEAL_LOW = 80
EXPOSURE_IDEAL_HIGH = 180
```

---

## 9. Honest Limitations

1. The scoring model is a linear weighted sum. It does not capture complex interactions between quality factors (e.g., a slightly blurry background is acceptable in portrait mode but not in landscape).

2. The face score treats "no face" as neutral. For portrait-heavy collections, users may want to adjust the weight.

3. The duplicate penalty is flat, not proportional to group size. A photo with 10 duplicates gets the same penalty as one with 2.

4. Aesthetic quality (composition, color harmony, visual interest) is not measured. The system evaluates technical quality only.

5. All thresholds are initial estimates based on general photographic conventions. Users should calibrate them for their specific use case.
