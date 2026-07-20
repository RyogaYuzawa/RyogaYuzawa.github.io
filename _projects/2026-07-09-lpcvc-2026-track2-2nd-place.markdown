---
layout: post
title: 2nd Place in IEEE Low Power Computer Vision Challenge 2026 Track 2 at CVPR 2026 Workshop
list_title: 2nd Place in IEEE Low Power Computer Vision Challenge 2026 Track 2 at CVPR 2026 Workshop
date: 2026-07-09
author: Ryoga Yuzawa
categories: [Project, Competition, Computer Vision]
tags: [LPCVC, Action Recognition, Video Recognition, Edge AI, Competition]
image: /assets/media/projects/lpcvc-2026-track2-2nd-place/award-certificate.jpg
description: "A short note on receiving 2nd place in the Action Recognition in Video track at LPCVC 2026."
keywords: "LPCVC 2026, action recognition, video recognition, edge AI, competition"
summary: "This project note records our result in the 2026 IEEE Low Power Computer Vision Challenge (LPCVC), held as part of the Efficient Deep Learning for Computer Vision workshop at Computer Vision and Pattern Recognition (CVPR) 2026."
---

## Overview
This project note records our result in the 2026 IEEE Low Power Computer Vision Challenge (LPCVC), held as part of the Efficient Deep Learning for Computer Vision workshop at CVPR 2026.

In the **Action Recognition in Video** track, our team **TEAM-ALPHA** placed **2nd**.

<figure>
  <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; align-items: center;">
    <img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/award-ceremony.jpg" alt="TEAM-ALPHA receiving the second-place award at the LPCVC 2026 ceremony" loading="lazy" style="width: 100%;">
    <div style="aspect-ratio: 2517 / 1303; display: flex; align-items: center; justify-content: center;">
      <img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/award-certificate.jpg" alt="IEEE Computer Society second-place award certificate for TEAM-ALPHA in LPCVC 2026 Track 2" loading="lazy" style="width: auto; height: 100%; max-width: 100%; object-fit: contain;">
    </div>
  </div>
  <figcaption style="text-align: center;">LPCVC 2026 at CVPR 2026 Efficient Deep Learning for Computer Vision Workshop</figcaption>
</figure>

The submitted model was evaluated on the Qualcomm Dragonwing IQ-9075 EVK through Qualcomm AI Hub.

<div class="content-image-right dragonwing-credit-image">
  <img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/qualcomm-dragonwing-chip.jpg" alt="Qualcomm Dragonwing chip" loading="lazy">
  <span class="image-credit">Credit: Qualcomm</span>
</div>

- **Model**: DecomposedVideoMAE (ViT-B, 112px, float)
- **Latency**: 19.322 ms on Dragonwing IQ-9075 EVK
- **LB Accuracy**: 96.776%

LPCVC 2026 attracted strong participation, with **229 teams** competing across all tracks.

<img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/participating-teams.jpg" alt="Chart showing the growth in LPCVC teams and submissions from 2018 to 2026" loading="lazy" style="width: 50%;">

## Solution

Our solution, **DecomposedVideoMAE**, is based on a Kinetics-710-pretrained VideoMAEv2 ViT-B<sup><a href="#ref-videomaev2">(1)</a></sup>. We decomposed its original Conv3d patch embedding into a Conv2d followed by a Conv3d, using SVD and MSE-based distillation to reproduce the original patch-embedding output. Training was performed in stages: the backbone was first frozen and then fully fine-tuned at 224px, after which logit and feature distillation transferred the model's knowledge to a more efficient 112px student.

<figure>
  <img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/decomposition-pipeline.png" alt="DecomposedVideoMAE patch-embedding distillation and fine-tuning pipeline" loading="lazy" style="width: 80%;">
  <figcaption style="text-align: center;">Patch-embedding decomposition, distillation, and fine-tuning pipeline.</figcaption>
</figure>

<figure>
  <a href="/assets/media/projects/lpcvc-2026-track2-2nd-place/videomae_decomposition_patch_profile.pdf" style="display: block;">
    <img src="/assets/media/projects/lpcvc-2026-track2-2nd-place/decomposition-compute-cycles.png" alt="Compute-cycle comparison between the original Conv3D patch projection and the decomposed Conv2D and Conv3D front end" loading="lazy" style="width: 80%;">
  </a>
  <figcaption style="text-align: center;">Compute cycles for the original Conv3D patch projection (left) and the decomposed Conv2D–Conv3D front end (right).</figcaption>
</figure>

For the final fitting stage, the training and validation sets were combined, and selected student checkpoints were averaged using Model Soup. The exported model also applies mathematically equivalent deployment optimizations: input normalization is fused into the Conv2d weights, attention scaling is absorbed into the query and key weights, and the input uses the channel-last NTHWC layout. The resulting float model achieved **96.776% leaderboard accuracy** with **19.322 ms latency** on the Qualcomm Dragonwing IQ-9075 EVK.

Our public code is available here:

{% include github-repo-card.html
  url="https://github.com/tasuku-takagi/LPCVC_2026_Track2_team-alpha"
  image="https://opengraph.githubassets.com/lpcvc2026/tasuku-takagi/LPCVC_2026_Track2_team-alpha"
  label="Public Code"
  title="LPCVC_2026_Track2_team-alpha"
  subtitle="tasuku-takagi"
%}

## Reference

<div id="ref-videomaev2"></div>

{% include link-card.html url="https://arxiv.org/abs/2303.16727" label="(1) VideoMAE V2: Scaling Video Masked Autoencoders with Dual Masking (CVPR 2023)" %}

{% include link-card.html url="https://lpcv.ai/2026LPCVC/winners/" label="LPCVC 2026 Winners" %}

{% include link-card.html url="https://ecv-workshop.github.io/" label="ECV @ CVPR 2026 Workshop" %}
