---
layout: post
title: MIPI Tx/Rx System Design on Zynq
date: 2025-04-02
author: Ryoga Yuzawa
categories: [FPGA,MIPI,Video Application]
tags: [FPGA, Xilinx, Zynq,MIPI]
image: /assets/media/posts/mipi-txrx-system-design/hero.png
description: "Learn how to implement MIPI CSI-2 Rx and DSI Tx subsystems on Xilinx Zynq FPGA. Complete guide with Vivado IP design and Vitis implementation."
keywords: "MIPI, CSI-2, DSI, FPGA, Zynq, Xilinx, Vivado, Vitis, Video Processing"
summary: "A system-design memo for bringing up MIPI video input and output on Xilinx Zynq platforms using the vendor-provided CSI-2 RX and DSI TX subsystems. The article walks through the role of the D-PHY, AXI Lite, and AXI-Stream interfaces, how to generate and inspect the Vivado example design, how to export the hardware into Vitis, and how to reuse the provided driver examples as a starting point for actual camera and display pipelines built on FPGA video IP."
---

## Introduction
This document is a memo on using Xilinx-provided IP, namely the MIPI CSI-2 Rx Subsystem and MIPI DSI Tx Subsystem.

### Environment
- **FPGA:** Xilinx ZCU102 (no physical validation)
- **OS:** WSL2 Ubuntu 20.04
- **Development Environment:** Vivado ML Edition 2021.2 for Windows

## Objective
Operate the MIPI Rx/Tx IP.

Reference Documentation (Xilinx official):

<a href="https://docs.xilinx.com/r/en-US/pg232-mipi-csi2-rx/Implementing-the-Example-Design" data-card-controls="0" class="embedly-card">Link</a>



## MIPI CSI-2 RX Subsystem IP
The subsystem receives the signal through the differential D-PHY layer and converts the video timing with the CSI2-RX controller into an AXI Lite interface. The Video Format Bridge block converts the video signal to an AXI-Stream. Consequently, two buses exist: AXI Lite and AXI-Stream.

- Timing format (HSync, VSync, etc.) is set via the IP Driver on Vitis.
- Video format (RGB888, YUV844, etc.) is set in the Vivado IP block design.
- Lane count and transmission rate are configured in Vivado.

![](/assets/media/posts/mipi-txrx-system-design/hero.png)

## MIPI CSI-2 Overview
MIPI CSI-2 is a differential signaling interface mainly used for image sensors and displays. The physical layer is D-PHY. The detailed specifications are not publicly available unless one is a member of the MIPI Alliance; specifications available online (e.g., the document from NXP on CIS) are referenced here.

<a href="https://www.nxp.com/docs/en/application-note/AN5305.pdf" data-card-controls="0" class="embedly-card">Link</a>

![](/assets/media/posts/mipi-txrx-system-design/csi2-rx-subsystem.png)
![](/assets/media/posts/mipi-txrx-system-design/mipi-overview.png)

## Project Implementation

### Implementation of the Vivado Example Design
- Create an empty project in Vivado by selecting the board "ZCU102".
- In the IP Catalog, double-click on the MIPI CSI-2 RX Subsystem IP.
- Switch to the Open Example Design tab and click Finish.
- The MIPI CSI-2 RX Subsystem appears in the Sources as an IP; right-click on it.
- Select "Create Example Design".
- Once the Block Design is completed, generate the Bitstream.
- Export Hardware by saving the XSA file to an appropriate directory.
- The block design created is as follows:

![](/assets/media/posts/mipi-txrx-system-design/vivado-example-block-design.png)

### Importing the Example Design into Vitis
- Launch Vitis.
- Create an Application by selecting the generated XSA file as the platform.
- Choose an Empty Application and click Finish.
- Open platform.spr and navigate to Board Support Package -> Drivers.
- Import examples for csirx_0 / mipiciss by checking the sp701 folder and clicking OK.

![](/assets/media/posts/mipi-txrx-system-design/vitis-driver-import.png)
![](/assets/media/posts/mipi-txrx-system-design/vitis-driver-import-checked.png =400x)

- Multiple files, including xmipi_sp701_example.c, will be imported.
- For actual usage, right-click the project and build it.
- Launch the hardware debug session by selecting Run As / Debug As -> Launch Hardware.

## Hardware Block

### Preliminaries
- The Display Port on the Zynq Ultrascale+ is on the PS side.
- HDMI/DSI ports are on the PL side.
- Only HDMI/DSI will be used in hardware; no need to input Display signals into the Zynq PS.

### Zynq MPSoC
![](/assets/media/posts/mipi-txrx-system-design/hardware-block-1.png)
![](/assets/media/posts/mipi-txrx-system-design/hardware-block-2.png)

### HDMI Display Path
![](/assets/media/posts/mipi-txrx-system-design/hardware-block-3.png)

### DSI Display Path
![](/assets/media/posts/mipi-txrx-system-design/hardware-block-4.png)

#### MIPI DSI Tx IP Configuration
- The DSI Tx IP supports DCS LP Command mode, but appears to be receive-only (no Tx).
- For devices that require DCS command triggering during the initialization sequence, a separate IP for DCS command Tx might be necessary.
- When controlling MIPI with Xilinx FPGA, the Video Timing Controller is not used; instead, Vsync/Hsync signals are controlled by the Zynq side via AXI-Lite.
- The video signal is sent over an AXI-Stream, separate from the control signals.
- The operations performed in the DSI Display path are essentially the same as those on the CSI-2 Rx Subsystem for CMOS image sensor input.

![](/assets/media/posts/mipi-txrx-system-design/dsi-tx-1.png)

#### Pin Assignment
![](/assets/media/posts/mipi-txrx-system-design/dsi-tx-2.png)

Pins can be assigned from the HP ports. On the ZCU102 evaluation board, the available HP ports are connected to the FMC connector. In cases where an evaluation board does not expose HP ports, assignment must be performed in the constraints file.

→ For Zynq Ultrascale devices, the MIPI Subsystem IP displays the Pin Assignment tab. On Zynq-7000 devices, the Pin Assignment tab might not be available, requiring manual pin assignment in the constraints file. In such cases, the I/F is LP mode: HSUL_12 / HS mode: LVDS_25.

The diagram below shows the pin assignment for ZCU102. Numerous HP ports are available (according to Xilinx official documentation):

![](/assets/media/posts/mipi-txrx-system-design/dsi-tx-3.png)

Refer to the following for additional details:  
AR# 67963: Zynq UltraScale+ MPSoC ZCU102 Evaluation Kit - UG1182 (v1.0) - Correction of FMC Pinout  
<a href="https://support.xilinx.com/s/article/67963?language=ja" data-card-controls="0" class="embedly-card">Link</a>



### Constraints File
Reviewing the constraints file reveals that there is no assignment for CSI-2 Rx/DSI Tx, meaning that these must be configured within the IP customization in the Block Design. Only the sensor initialization using I2C and the GPIO settings for DSI Display are configured.

I2C pull-ups are implemented on the FPGA side.

```tcl
# CSI-2 Rx Subsystem Related constraints

# Sensor IIC
set_property PULLUP true [get_ports IIC_sensor_scl_io]
set_property PULLUP true [get_ports IIC_sensor_sda_io]
set_property PACKAGE_PIN L15 [get_ports IIC_sensor_scl_io]
set_property PACKAGE_PIN K15 [get_ports IIC_sensor_sda_io]
set_property IOSTANDARD HSUL_12_DCI [get_ports IIC_sensor_scl_io]
set_property IOSTANDARD HSUL_12_DCI [get_ports IIC_sensor_sda_io]

# GPIO Configuration
set_property PACKAGE_PIN M14 [get_ports {GPIO_sensor_tri_o[0]}]
set_property PACKAGE_PIN M10 [get_ports {GPIO_sensor_tri_o[1]}]
set_property PACKAGE_PIN AA12 [get_ports {GPIO_sensor_tri_o[2]}]

set_property IOSTANDARD LVCMOS12 [get_ports {GPIO_sensor_tri_o[*]}]

# DSI GPIO Display
set_property PACKAGE_PIN L12 [get_ports {gpio_display_tri_o[0]}]
set_property PACKAGE_PIN K12 [get_ports {gpio_display_tri_o[1]}]

set_property IOSTANDARD LVCMOS12 [get_ports {gpio_display_tri_o[*]}]
```

After verifying the constraints file, perform the following:
- Create the HDL Wrapper and generate the Bitstream.
- Export Hardware.


## Conclusion
Comments and corrections are welcome!
