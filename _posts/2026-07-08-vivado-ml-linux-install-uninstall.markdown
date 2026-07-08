---
layout: post
title: Installing and Uninstalling Vivado ML on Linux
date: 2023-07-09
author: Ryoga Yuzawa
categories: [FPGA, Vivado, Linux]
tags: [Vivado, Linux, Installation, Uninstallation, FPGA, Xilinx]
description: "A practical note on installing and uninstalling Vivado ML on Linux, including the basic setup flow and removal procedure."
keywords: "Vivado ML, Linux, Installation, Uninstallation, FPGA, Xilinx, Ubuntu"
summary: "A short practical memo on installing and uninstalling Vivado ML on Linux. The article covers the need for a GUI environment, where to obtain the Linux installer, how to grant execution permission and run the installer, the difference between choosing Vitis and Vivado in the installer flow, and how to launch the uninstaller later when cleanup is needed."
---

## Introduction
This is a short memo on how to install and uninstall Vivado ML on Linux.

## Installation
As a prerequisite, a GUI environment is required.

- Go to the following page and download the Linux version of Vivado ML Edition:

<https://japan.xilinx.com/support/download.html>

- Move to the downloaded directory from the Linux side.
- Grant execution permission and run the installer:

```bash
sudo chmod +x Xilinx_Unified_2019.2_1106_2127_Lin64.bin
sudo ./Xilinx_Unified_2019.2_1106_2127_Lin64.bin
```

In most cases, choosing `Install Vitis` will also install Vivado at the same time.

Previously, when I selected only `Vivado`, Vitis was not installed, so that choice mattered.

## Uninstallation
Launch the uninstaller with the following command and proceed through the removal flow:

```bash
sudo /tools/Xilinx/.xinstall/Vitis_2019.2/xsetup -Uninstall
```
