---
layout: post
title: Creating a Pattern Display Circuit with Vitis HLS High-Level Synthesis
date: 2023-04-26
author: Ryoga Yuzawa
categories: [FPGA, VitisHLS, Zybo]
tags: [VitisHLS, FPGA, Zybo, High-Level Synthesis]
image: /assets/media/posts/hls-pattern-circuit/hero.png
description: "Learn how to create pattern display circuits using Vitis HLS high-level synthesis. Complete guide with C-RTL cosimulation and waveform analysis."
keywords: "Vitis HLS, High-Level Synthesis, FPGA, Pattern Display, C-RTL Cosimulation, Waveform Analysis"
summary: "A hands-on note focused on creating a pattern drawing circuit with Vitis HLS and validating how the synthesized hardware actually behaves. The article follows the flow from project creation and C-based test bench setup through synthesis, C-RTL cosimulation, and waveform inspection in Vivado, using a rectangle fill example to show how image data is generated, how AXI burst transfers appear on the bus, and how to confirm timing and overlap behavior from the resulting traces."
---

## Introduction
This post continues from the previous one, documenting the practical application of "High-Level Synthesis Applications" from Chapter 11-1 onward in ["FPGA Programming Complete Guide, 2nd Edition"](https://www.amazon.co.jp/FPGA%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E5%A4%A7%E5%85%A8-Xilinx%E7%B7%A8-%E7%AC%AC2%E7%89%88-%E5%B0%8F%E6%9E%97-%E5%84%AA/dp/4798063266).

## Environment

- **FPGA**: Xilinx Zybo Z7-20
- **OS**: WSL2 Ubuntu 20.04
- **Development Environment**: Vivado ML edition 2022.1 Linux

## Objective

Using Vitis HLS, create a pattern display circuit through high-level synthesis.

## Implementation

### Project Creation

- Launch Vitis HLS and add Source and Test Bench files
- Execute "Build selected file"
- Perform "C Synthesis"

Below is an excerpt of the test bench code using the `patblt` function to draw rectangles and write to an `imagedata.raw` file:

{% highlight c %}
int main() {
    for (int i = 0; i < XSIZE * YSIZE; i++) {
        VRAM[i] = 0;
    }

    patblt(VRAM,   0,   0, 320, 240, 0x00ff0000);
    patblt(VRAM, 160, 120, 320, 240, 0x0000ff00);
    patblt(VRAM, 320, 240, 320, 240, 0x000000ff);

    FILE *fd = fopen("imagedata.raw", "wb");

    for (int y = 0; y < YSIZE; y++) {
        for (int x = 0; x < XSIZE; x++) {
            int temp = VRAM[y * XSIZE + x];
            fprintf(fd, "%c", (temp >> 16) & 0xff);
            fprintf(fd, "%c", (temp >> 8 ) & 0xff);
            fprintf(fd, "%c", (temp      ) & 0xff);
        }
    }
    fclose(fd);

    return 0;
}
{% endhighlight %}


### C-RTL Cosimulation

- After synthesis completion, execute "Cosimulation"
- Choose "Dump Trace: All" in the options and click "OK"
- Upon completion, the following summary appears:

![Cosimulation Summary](/assets/media/posts/hls-pattern-circuit/cosim-summary.png)

- Select "Open Wave Viewer" to launch Vivado

### Waveform Analysis

- Simulation finished in approximately 2.732ms
- From the waveform, the burst length is confirmed to be 16 (`m_axi_gmem_AWLEN[7:0] = 0x0f`)
- Address (`gmem_AWADDR[63:0]`) is issued without waiting for the completion of WDATA transfers, indicating overlap transfer (this is difficult to observe clearly due to fixed WDATA values, refer to page 358, "Introduction to AXI Bus" in the book)

Overall waveform:
![Waveform overview](/assets/media/posts/hls-pattern-circuit/hero.png)

Detailed waveform:
![Waveform detail](/assets/media/posts/hls-pattern-circuit/waveform-detail.png)

### Verification of Saved Image Data

Displaying the saved `imagedata.raw` confirmed that the intended image is correctly drawn.

![Generated image data](/assets/media/posts/hls-pattern-circuit/generated-image-data.png)

### IP Generation

- Execute "Export RTL" and save as IP

## Conclusion

In this post, a simple pattern display circuit was created using Vitis HLS high-level synthesis. AXI bus transfer behaviors were validated through waveform simulation, and the generated image data was confirmed to match the intended design. Future work will involve deploying the generated IP onto the actual Zybo Z7-20 FPGA for further verification.
