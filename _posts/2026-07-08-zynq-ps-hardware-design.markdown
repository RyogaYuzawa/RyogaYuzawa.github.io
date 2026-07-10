---
layout: post
title: Building a Hardware System with Zynq PS
date: 2023-03-28
author: Ryoga Yuzawa
categories: [FPGA, Zynq, Vivado]
tags: [Zynq, FPGA, Vivado, Processing System, Hardware Design, Xilinx]
image: /assets/media/posts/zynq-ps-hardware-design/block-design.png
description: "A practical note on building a hardware system with the Zynq Processing System, including block design setup, GPIO configuration, and hardware integration."
keywords: "Zynq, FPGA, Vivado, Processing System, Hardware Design, Xilinx, Block Design, GPIO"
summary: "A practical engineering note on constructing a hardware system around the Zynq Processing System. The article covers setting up a Zynq PS-based block design in Vivado, adding AXI GPIO for LED and button control, running connection automation, matching ports to constraints, and understanding the warning related to DDR-to-PS clock skew before generating the HDL wrapper for the design."
---

## Introduction
Continuing from the previous post, this article documents the "Hard Macro CPU System" section from *FPGA Programming Complete Guide, 2nd Edition*.

At this point, my HDL experience was still limited to spending about a day reading an introductory Verilog book and learning only the basic syntax.

## Environment
- **FPGA**: Xilinx Zybo Z7-20
- **OS**: WSL2 Ubuntu 20.04
- **Development Environment**: Vivado ML Edition 2022.1 for Linux


## Objective
- Control the PL side from the Zynq PS and drive the LEDs
- Use GPIO as input so that the system can be controlled externally

Reference:

{% include link-card.html url="https://docs.xilinx.com/v/u/ja-JP/ug585-Zynq-7000-TRM" label="Zynq-7000 Technical Reference Manual" %}

## Implementation

### Hardware Construction
- Create an empty project in Vivado
- `Create Block Design → Add IP` and add the Zynq PS
- Add `AXI GPIO`, switch it to a 2-channel configuration, and set:
  - Output → `LED_RGB[2:0]`
  - Input → `BTN[1:0]`
- Run `Connection Automation` so that `System Reset` and `AXI Interconnect` are added automatically
- Rename the ports to match the constraints file
- Run `Validate Design`

![Zynq PS block design](/assets/media/posts/zynq-ps-hardware-design/block-design.png)

A warning appeared, but the cause was that the skew between the DDR memory and the PS clock had become negative.

Checking the DDR skew settings inside the Zynq PS showed that they matched the negative values mentioned in the warning:

![DDR skew warning](/assets/media/posts/zynq-ps-hardware-design/ddr-skew-warning.png)

Once the block design is complete, select the design and run `Create HDL Wrapper`. This generates `design_wrapper.v` under the design sources.
