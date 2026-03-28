---
id: "009"
title: "Design ML data collection strategy for scam classification"
status: "todo"
area: "backend"
agent: "@systems-architect"
priority: "normal"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: ["014"]
blocked_by: []
---

## Description

Design the data collection and preparation strategy for the future ML/DL scam classification model. The developer plans to collect data from the live platform over ~1 month and combine it with public datasets to train a model that can auto-classify whether a report is likely fraud.

This task covers the architecture and strategy — not the model implementation itself (that's #014).

## Acceptance Criteria

- [ ] Data collection requirements documented (what fields, what volume needed)
- [ ] Data schema for ML training defined (features, labels, format)
- [ ] Public dataset sources identified and evaluated
- [ ] Data pipeline design: how production data flows to training data
- [ ] Privacy considerations addressed (anonymization of training data)
- [ ] Strategy documented in `docs/technical/` or as an ADR

## Technical Notes

- Current scammer reports have: name, phone, email, social links, evidence text, scam type, admin verdict (approved/rejected)
- The admin verdict (approved/rejected) can serve as labels for supervised learning
- Need sufficient volume of both positive and negative examples
- Consider data augmentation strategies if volume is low

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
