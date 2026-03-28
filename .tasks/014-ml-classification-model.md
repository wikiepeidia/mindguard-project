---
id: "014"
title: "Implement ML/DL scam classification model"
status: "todo"
area: "backend"
agent: "@backend-developer"
priority: "low"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: []
blocked_by: ["009"]
---

## Description

Implement a machine learning / deep learning model to automatically classify whether a scammer report is likely genuine fraud. This replaces manual admin review with AI-assisted classification. Blocked by #009 (data collection strategy) and requires sufficient training data (~1 month of production data collection + public datasets).

This is explicitly a v2 feature — deferred from v1 due to insufficient training data.

## Acceptance Criteria

- [ ] Model trained on collected production data + public datasets
- [ ] Model achieves acceptable precision/recall for fraud classification
- [ ] Integration endpoint in Flask app for real-time classification
- [ ] Admin dashboard shows model confidence alongside manual review
- [ ] Model performance metrics logged and monitored
- [ ] Fallback to manual review when model confidence is low

## Technical Notes

- Features: report text, scam type, contact info patterns, reporter history
- Labels: admin approval/rejection decisions
- Consider: scikit-learn for initial model, upgrade to deep learning if volume justifies
- Model should augment, not replace, admin review — show confidence score alongside verdict
- Data privacy: ensure training data is properly anonymized

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
