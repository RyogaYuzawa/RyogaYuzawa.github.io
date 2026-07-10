---
layout: post
title: 2nd Place in IEEE Low Power Computer Vision Challenge 2026 Track 2
date: 2026-07-09
author: Ryoga Yuzawa
categories: [Project, Competition, Computer Vision]
tags: [LPCVC, Action Recognition, Video Recognition, Edge AI, Competition]
image: /assets/media/projects/lpcvc-2026-track2-2nd-place/qualcomm-dragonwing-chip.jpg
description: "A short note on receiving 2nd place in the Action Recognition in Video track at LPCVC 2026."
keywords: "LPCVC 2026, action recognition, video recognition, edge AI, competition"
summary: "This project note records our 2nd place result in the Action Recognition in Video track at the 2026 IEEE Low Power Computer Vision Challenge, with links to the official winners page and the public code repository."
---

## Overview
This project note records our result in the 2026 IEEE Low Power Computer Vision Challenge (LPCVC).

In the **Action Recognition in Video** track, our team **TEAM-ALPHA** placed **2nd**. The official winners page lists the team as:

- **Team**: `TEAM-ALPHA`
- **Place**: `2nd Place`
- **Location**: `Japan`
- **Organization**: `Sony Corporation`

Reference:

- [LPCVC 2026 Winners](https://lpcv.ai/2026LPCVC/winners/)

## Public Code
The implementation has been published here:

- [tasuku-takagi/LPCVC_2026_Track2_team-alpha](https://github.com/tasuku-takagi/LPCVC_2026_Track2_team-alpha)

## Competition
This result was achieved in the following track:

- **Challenge**: `2026 IEEE Low Power Computer Vision Challenge`
- **Track**: `Track 2: Action Recognition in Video`
- **Submission Window**: `March 1, 2026 12:00 AM ET` to `April 30, 2026 11:59 PM ET`
- **Sponsor**: `Qualcomm Technologies, Inc.`
- **Hardware Platform**: `Qualcomm Dragonwing IQ-9075 EVK`
- **Software Platform**: `Qualcomm AI Hub`

## Deployment Platform
Submitted models were evaluated on `Qualcomm Dragonwing IQ-9075 EVK` through `Qualcomm AI Hub`.

<img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/qualcomm-dragonwing-chip.jpg" alt="Qualcomm Dragonwing chip" width="33%">

## Rule Summary
- The task was to classify the exercise action in a video clip.
- The model input was a `16-frame` clip.
- Test data was `Hidden QEVD`, and sample data was `QEVD`.
- Submitted models were evaluated online through `Qualcomm AI Hub`.
- Stage 1 required execution time faster than `34 ms`.
- Stage 2 ranked valid submissions by classification accuracy.
- The sample solution was based on `ResNet-2Plus1D`.
- Prize amounts were `$6,000` for champion, `$3,000` for 2nd place, and `$1,000` for 3rd place.

## Evaluation Data Format
- Input videos were `.mp4` files of about `2` to `10` seconds.
- Audio was ignored.
- `16` frames were sampled from each video.
- Frames were prepared as a tensor in `(C, T, H, W)` format.
- The evaluation pipeline used preprocessing including resize to `128 x 171`, center crop to `112 x 112`, and normalization with fixed RGB mean and standard deviation.

## Result
- Achieved **2nd Place** in `Track 2: Action Recognition in Video`
- Published the code used for the challenge
- Added the official competition result and repository link for reference

## Notes
I plan to expand this page later with more details about the approach, model design, and what worked well during the competition.
