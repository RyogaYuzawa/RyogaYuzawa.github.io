---
layout: post
title: 2nd Place in IEEE Low Power Computer Vision Challenge 2026 Track 2 at CVPR 2026 Workshop
list_title: 2nd Place in IEEE Low Power Computer Vision Challenge 2026 Track 2 at CVPR 2026 Workshop
date: 2026-07-09
author: Ryoga Yuzawa
categories: [Project, Competition, Computer Vision]
tags: [LPCVC, Action Recognition, Video Recognition, Edge AI, Competition]
image: /assets/media/projects/lpcvc-2026-track2-2nd-place/qualcomm-dragonwing-chip.jpg
description: "A short note on receiving 2nd place in the Action Recognition in Video track at LPCVC 2026."
keywords: "LPCVC 2026, action recognition, video recognition, edge AI, competition"
summary: "This project note records our result in the 2026 IEEE Low Power Computer Vision Challenge (LPCVC), held as part of the Efficient Deep Learning for Computer Vision workshop at Computer Vision and Pattern Recognition (CVPR) 2026."
---

## Overview
This project note records our result in the 2026 IEEE Low Power Computer Vision Challenge (LPCVC), held as part of the Efficient Deep Learning for Computer Vision workshop at CVPR 2026.

In the **Action Recognition in Video** track, our team **TEAM-ALPHA** placed **2nd**. The submitted model was evaluated on the Qualcomm Dragonwing IQ-9075 EVK through Qualcomm AI Hub.

<img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/qualcomm-dragonwing-chip.jpg" alt="Qualcomm Dragonwing chip" width="16%" style="float: right; margin: 0 0 1rem 1rem;">

- **Model**: DecomposedVideoMAE (ViT-B, 112px, float)
- **Latency**: 19.322 ms on Dragonwing IQ-9075 EVK
- **LB Accuracy**: 96.776%

## Reference

{% include link-card.html url="https://lpcv.ai/2026LPCVC/winners/" label="LPCVC 2026 Winners" %}

{% include link-card.html url="https://ecv-workshop.github.io/" label="ECV @ CVPR 2026 Workshop" %}

## Solutions (public code)
The implementation has been published here:

{% include github-repo-card.html
  url="https://github.com/tasuku-takagi/LPCVC_2026_Track2_team-alpha"
  image="https://opengraph.githubassets.com/lpcvc2026/tasuku-takagi/LPCVC_2026_Track2_team-alpha"
  label="Public Code"
  title="LPCVC_2026_Track2_team-alpha"
  subtitle="tasuku-takagi"
%}
