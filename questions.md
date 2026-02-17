# Questions for Original Study Team

## Data Analysis Decisions

### 1. PPG Channel Selection
**Question:** Which PPG channel was used for the original TABLE 1 analysis?

**Context:**
- EmotiBit provides three PPG channels: PI (infrared), PR (red), PG (green)
- Example scripts mention 'PG' in comments but don't confirm actual usage
- Standard cardiac analysis typically uses PI (infrared) for HR/SpO2

**Current assumption:** Using **PG (green)** based on example/ code comments

**Impact:** May affect direct comparison with original results

---

### 2. Study Design Confirmation
**Question:** Do participants complete both intervention AND control, or are they randomly assigned to one?

**Context:**
- Paper states: "participants were randomly assigned to an intervention group... or to a control group"
- Need to confirm for statistical test selection:
  - Within-subject: paired t-tests (baseline vs day2)
  - Between-subject: unpaired t-tests (intervention vs control)

**Current assumption:** Random assignment (between-subject design)

**Impact:** Determines which statistical tests to use

---

_Last updated: 2026-02-17_
