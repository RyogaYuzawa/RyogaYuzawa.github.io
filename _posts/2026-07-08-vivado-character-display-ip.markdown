---
layout: post
title: Designing a Character Display Circuit and Custom IP with Vivado
date: 2023-04-02
author: Ryoga Yuzawa
categories: [FPGA, Vivado, Zynq]
tags: [Vivado, FPGA, Zynq, Character Display, Custom IP, HDL, IP Design]
image: /assets/media/posts/vivado-character-display-ip/simulation-output.png
description: "A practical note on designing a character display circuit and building it as a custom IP in Vivado, including VRAM and CGROM generation, simulation, and verification."
keywords: "Vivado, FPGA, Zynq, Character Display, Custom IP, HDL, IP Design, AXI, Xilinx"
summary: "A practical engineering note on designing a character display circuit in Vivado and packaging it as a custom IP block. The article covers the required display specification, creation of VRAM and CGROM memory blocks using Vivado IP, repackaging of the character display circuit, and simulation-based verification of memory writes and displayed RGB output before moving on to hardware validation."
---

## Introduction
Continuing from the previous post, this article documents the "Pre-verification and Hardware Validation of a Character Display Circuit" section from *FPGA Programming Complete Guide, 2nd Edition*.

As a continuation of the previous article, I designed a character display circuit, packaged it as an IP block, and prepared it to run on FPGA hardware.

## Environment
- **FPGA**: Xilinx Zybo Z7-20
- **OS**: WSL2 Ubuntu 20.04
- **Development Environment**: Vivado ML Edition 2022.1 for Linux

## Objective
Create a circuit that displays characters on a monitor through HDMI.

### Character Display Circuit Specification
- One character is composed of an `8 x 8` dot matrix
- Up to 80 characters horizontally and 80 lines vertically can be displayed
- VRAM is used to store character codes and character colors
- CGROM is used as a read-only memory that stores character patterns

## Implementation

### Project Creation
- `Project Creation → Create and Package New IP`
- `Package a Specified Directory`
- Select the `chardisp_ip` directory from the appendix and click `Finish`

![Package specified directory](/assets/media/posts/vivado-character-display-ip/package-specified-directory.png)

At this stage, VRAM and CGROM are still missing.

### Generating VRAM
- Add the `Block Memory Generator` IP
- Customize the IP
  - **Memory Type**: `True Dual Port RAM`
    Two ports are required because one side is used for display-timing reads and the other side is used for CPU read/write access through the AXI bus.
  - **Byte Write Enable**: `ON`
  - **Byte Size**: `8 bits`
    The VRAM data width is 24 bits, but this allows writes in 8-bit units.
  - **Port A/B**:
    - Write/Read Width: `24 bits`
    - Write/Read Depth: `4096`
  - **Enable Port Type**: `Always Enabled`

![VRAM customization 1](/assets/media/posts/vivado-character-display-ip/vram-customize-1.png)
![VRAM customization 2](/assets/media/posts/vivado-character-display-ip/vram-customize-2.png)

Check the summary and click OK.

- Run `Out of Context per IP → Generate` to create the VRAM block.

### Generating CGROM
- Add the `Block Memory Generator` IP
- Customize the IP
  - **Memory Type**: `Single Port ROM`
  - **Port A Width**: `8 bits`
  - **Port A Depth**: `1024`
  - **Enable Port Type**: `Always Enabled`
  - **Other Options / Memory Initialization**: enable `Load Init File`
  - Select the `.coe` file (`CGDATA.coe`)

![CGROM customization](/assets/media/posts/vivado-character-display-ip/cgrom-customize.png)

Check the summary and click OK, then generate the block.

### Re-Packaging the IP

![Re-package IP](/assets/media/posts/vivado-character-display-ip/repackage-ip.png)

At this point, the character display circuit IP is complete.

![Character display IP in catalog](/assets/media/posts/vivado-character-display-ip/ip-catalog-entry.png)

Now `chardisp_ip` can be called from the IP Catalog.

## Simulation of the Character Display Circuit
- Create a new project for simulation
- Create a test bench that writes values into memory and outputs a file
  - The overall procedure is the same as the earlier pattern display circuit design

Reference:
<https://zenn.dev/ryo_tan/articles/464484ae3de8e0>

![Simulation hierarchy](/assets/media/posts/vivado-character-display-ip/simulation-hierarchy.png)

If the hierarchy looks like this, the setup is OK.

### Run Simulation

![Simulation waveform 1](/assets/media/posts/vivado-character-display-ip/simulation-waveform-1.png)
![Simulation waveform 2](/assets/media/posts/vivado-character-display-ip/simulation-waveform-2.png)

At `5.1 us`, reset is released, write enable goes high, and data seems to be fetched from the CGROM.

![Simulation waveform 3](/assets/media/posts/vivado-character-display-ip/simulation-waveform-3.png)

Around `0.85 ms`, the memory write data has completed.

![Simulation waveform 4](/assets/media/posts/vivado-character-display-ip/simulation-waveform-4.png)

After `VGA_DE` goes high, RGB logic begins changing around `2.7 ms`, which shows that the image is being displayed as intended.

Check the written data with IrfanView:

![Simulation output image](/assets/media/posts/vivado-character-display-ip/simulation-output.png)

Simulation completed successfully.

## Next Step
The next step is hardware validation on the actual board.
