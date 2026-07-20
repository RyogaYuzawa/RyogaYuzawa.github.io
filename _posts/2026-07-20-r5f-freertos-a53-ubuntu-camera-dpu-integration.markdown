---
layout: post
title: Designing a Heterogeneous Multi-Core Camera AI System with Ubuntu on Cortex-A53 and FreeRTOS on Cortex-R5F
date: 2026-07-20
author: Ryoga Yuzawa
categories: [FPGA, Zynq MPSoC, Camera, AI]
tags: [Zynq MPSoC, FPGA, KV260, Cortex-A53, Cortex-R5F, FreeRTOS, Ubuntu, DPU, Camera, OpenAMP, RPMsg]
description: "Integrating FreeRTOS on the Cortex-R5F into an Ubuntu-based camera and DPU pipeline running on the Cortex-A53 of the AMD Kria KV260."
keywords: "Zynq MPSoC, KV260, Cortex-A53, Cortex-R5F, FreeRTOS, Ubuntu, Camera, DPU, Vitis AI, OpenAMP, RPMsg"
summary: "A practical guide to adding a Cortex-R5F FreeRTOS control domain to a Cortex-A53 Ubuntu camera and DPU pipeline using OpenAMP and RPMsg."
image: /assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/AMD+Zynq+MPSoC.jpg
---

## Introduction

<div class="article-logo-right">
  <img src="/assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/AMD+Zynq+MPSoC.jpg" alt="AMD Zynq MPSoC logo">
  <span>Source: <a href="https://www.amd.com/en/products/adaptive-socs-and-fpgas/soc/zynq-ultrascale-plus-mpsoc.html">AMD</a></span>
</div>

The original KV260 system runs camera capture, FPGA ISP, preprocessing, DPU inference, postprocessing, and display on the Cortex-A53 under Ubuntu. This is practical for vision development, but a best-effort Linux process cannot guarantee fixed-rate control when inference becomes late or stops.

The initial objective was to make the camera pipeline itself real-time under FreeRTOS. However, **the ISP and DPU are accessed through Ubuntu drivers, OpenCL/XRT, and the Vitis AI Library.** **Moving the complete path to FreeRTOS would require major changes to accelerator control, memory management, interrupts, and model execution—effectively redesigning the camera and AI stack.**

**The chosen design accepts jitter in the Ubuntu camera/DPU domain and contains it at a real-time boundary on the R5F.** Timestamped results are checked by a fixed-period task that discards late data, monitors the Linux heartbeat, and selects the appropriate control or fail-safe response. Camera capture and inference are not made hard real-time; their non-deterministic timing is prevented from directly controlling the output.

This project adds FreeRTOS on the Cortex-R5F and divides the system into two execution domains:

- Ubuntu on the Cortex-A53 continues to own the camera, FPGA accelerators, Vitis AI runtime, postprocessing, display, and performance monitoring.
- FreeRTOS on the Cortex-R5F receives compact inference results and runs a deterministic 10 ms control task.
- OpenAMP/RPMsg carries fixed-size vision results, heartbeats, and control status between the processors.

Frames remain in the PL and DDR video path; only compact control information crosses RPMsg. This article documents the complete physical-KV260 bring-up and extends [Building a Camera ISP-DPU IP Pipeline from Scratch with AMD FPGA]({% post_url 2026-07-13-zynq-mpsoc-camera-isp-dpu-pipeline %}).

## Development Environment

| Component | Configuration |
|---|---|
| Target | AMD Kria KV260 with Zynq UltraScale+ MPSoC |
| Application processor | Quad-core Arm Cortex-A53 running Ubuntu 22.04 LTS |
| Real-time processor | Dual-core Arm Cortex-R5F; this design uses `psu_cortexr5_0` with FreeRTOS |
| Target kernel | `linux-xlnx` 5.15 |
| FPGA and firmware tools | Vivado 2024.2 and Vitis 2024.2 |
| Interprocessor transport | OpenAMP, remoteproc, virtio, RPMsg, and `rpmsg-char` |
| Camera AI workload | IMX219, FPGA ISP and preprocessing, DPU, postprocessing, and DisplayPort |

The repository implementation described here is located under `sw/r5f-camera-dpu` and is built against the XSA exported from the camera/DPU hardware design.

## System Architecture

The Zynq UltraScale+ MPSoC processing system combines an Application Processing Unit based on Arm Cortex-A53 cores with a Real-Time Processing Unit based on Arm Cortex-R5F cores, alongside shared memory, system functions, peripherals, and programmable logic. This provides the hardware foundation for partitioning one application across Linux-class and real-time processing domains.

![AMD Zynq UltraScale+ MPSoC block diagram showing the Application Processing Unit, Real-Time Processing Unit, memory, system functions, connectivity, and programmable logic](/assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/2617829-zynq-cg-block.avif)

*Zynq UltraScale+ CG family block diagram. Source: [AMD, Zynq UltraScale+ MPSoCs](https://www.amd.com/en/products/adaptive-socs-and-fpgas/soc/zynq-ultrascale-plus-mpsoc.html#productAdvantages). The diagram is included to illustrate the APU/RPU partition; the KV260's K26 device used in this project has the quad-core Cortex-A53 configuration listed in the development environment above.*

**The central objective of this implementation is communication between heterogeneous operating-system domains:** Ubuntu runs the camera and DPU application on the Cortex-A53, while FreeRTOS runs deterministic monitoring and control on the Cortex-R5F. OpenAMP/RPMsg connects these two software environments without moving image frames out of the existing PL and DDR video path.

The partition is deliberately asymmetric. Linux manages the high-level vision stack and hardware accelerators because V4L2, XRT, Vitis AI, and the display stack already run there. The R5F performs only the small amount of work that benefits from deterministic scheduling.

![Cortex-A53 Ubuntu camera and DPU pipeline connected over OpenAMP/RPMsg to Cortex-R5F FreeRTOS control tasks](/assets/media/posts/zynq-mpsoc-camera-isp-dpu-pipeline/images/a53-r5f-pipeline.svg)

The Cortex-A53 domain owns:

- Linux camera and media-controller configuration;
- the ISP output and camera timestamps;
- preprocessing, VART, DPU execution, and model postprocessing;
- conversion of detections into the fixed-size wire protocol;
- the RPMsg publisher, display, logging, and profiling.

The Cortex-R5F domain owns:

- a 10 ms periodic control task;
- a mailbox containing only the newest usable result;
- heartbeat, result-age, sequence, and frame-gap checks;
- the `INIT`, `FRESH`, `HOLD`, and `FAILSAFE` policy;
- a board-specific output hook for future GPIO or PWM control;
- best-effort control-status telemetry returned to Linux.

The R5F does not maintain a FIFO of every inference result. Control needs the newest valid observation, not a backlog of old decisions. The RPMsg receive callback validates a packet and copies it into a latest-value slot. It does not execute the control policy. The higher-priority periodic task reads the slot independently, so a busy transport cannot directly block the control deadline.

## Bring-Up Strategy

The integration was divided into independent gates. Starting the camera, DPU, remoteproc, and RPMsg simultaneously would make it difficult to determine which layer caused a failure.

![Seven-stage bring-up flow from target memory audit to camera and DPU integration](/assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/bringup-flow.svg)

**Bring-Up Order.** Each layer is gated independently before the camera and DPU workload is added. Starting with the complete camera pipeline would make memory, IPI, RPMsg, and application failures difficult to isolate.

The working order was:

1. Define the common message ABI and test the control policy without hardware.
2. Audit the live Device Tree, CMA, remoteproc, and IPI configuration on the KV260.
3. Reserve all R5F and RPMsg memory before Linux boots.
4. Generate the FreeRTOS application from the Vitis OpenAMP template.
5. Start only the R5F firmware through Linux remoteproc.
6. Verify the RPMsg name service and create an `rpmsg-char` endpoint.
7. Test fresh and stale synthetic results before connecting the camera application.
8. Run the existing camera/DPU pipeline while keeping the R5F active.
9. Publish real inference results from the camera application.

This sequence was essential during bring-up. A `running` remoteproc state alone does not prove that memory carveouts, the IPI interrupt, the RPMsg name service, and bidirectional packet transfer all work.

## Fixed-Size Message Protocol

The common header is defined as a C-compatible ABI and included by both the A53 C++ application and the R5F C++ firmware. Fixed-width integers and compile-time size checks prevent accidental layout changes.

Three message types are used.

### `VISION_RESULT`

A vision result contains the frame sequence, capture timestamp, inference-completion timestamp, validity interval, detection count, target coordinates, confidence, and diagnostic flags. It does not contain image pixels.

Coordinates and confidence values use Q16.16 fixed-point representation, avoiding any dependency on a floating-point ABI across processors. The A53 also supplies `source_age_us`, which is the time already consumed between capture and transmission. The R5F can therefore calculate result freshness without synchronizing its clock to Linux:

```text
result age = source_age_us + elapsed time since R5F reception
```

### `HEARTBEAT`

The heartbeat carries the A53 publisher uptime, health flags, and a non-zero `sender_instance` value that changes whenever the process restarts. Message sequence numbers return to one after a restart, so the R5F uses the instance change to discard sequence history and the latest value from the previous session.

### `CONTROL_STATUS`

The R5F returns its current control state, applied message sequence, result age, fault bits, drop and overwrite counters, control-task deadline misses, and maximum observed lateness. Telemetry uses `rpmsg_trysend()` and is allowed to drop when a vring is full; reporting must never make the deterministic task wait for Linux.

The common header, vision result, and control status are each 48 bytes, while a heartbeat is 16 bytes. Compile-time assertions keep every complete packet below the 496-byte RPMsg payload available from a 512-byte OpenAMP buffer.

A simplified version of the ABI is shown below:

```cpp
struct r5cd_message_header {
    uint32_t magic;
    uint16_t version;
    uint16_t type;
    uint32_t payload_size;
    uint32_t sequence;
    uint64_t source_time_ns;
    uint64_t send_time_ns;
    // Clock domain, flags, CRC32, and reserved fields
};

struct r5cd_vision_result {
    uint32_t frame_sequence;
    uint32_t flags;
    uint64_t capture_time_ns;
    uint64_t inference_done_time_ns;
    uint32_t valid_for_us;
    // Detection count, target, confidence, and source age
};
```

Before touching the target, the ABI, decoder, publisher, policy, and Device Tree memory contract can be checked on the host:

```bash
cd /path/to/fpga_rtos_camera_ai
make -C sw/r5f-camera-dpu check
```

## FreeRTOS Task Design

The R5F application separates communication from control:

| Task | Priority | Behavior |
|---|---:|---|
| `r5cd-control` | 4 | Runs every 10 ms, evaluates freshness, changes state, and applies the output hook |
| `r5cd-rpmsg` | 2 | Initializes OpenAMP and the endpoint, then polls the transport |
| `r5cd-status` | 2 | Sends a best-effort status snapshot without blocking control |

The control task uses `vTaskDelayUntil()` to preserve a fixed release period. If it wakes later than its scheduled release, it increments a deadline-miss counter and records the maximum lateness.

The default policy values are:

| Parameter | Value | Purpose |
|---|---:|---|
| Control period | 10 ms | R5F evaluation period |
| Heartbeat HOLD threshold | 100 ms | Enter `HOLD` when the Linux heartbeat is delayed |
| Heartbeat FAILSAFE threshold | 300 ms | Enter `FAILSAFE` when the heartbeat stops |
| Result FAILSAFE threshold | 200 ms | Reject a result that remains stale for too long |
| Startup FAILSAFE threshold | 500 ms | Fail safely when no valid result arrives after boot |
| Maximum inference latency | 50 ms | Diagnose a late inference result and enter `HOLD` |
| Maximum frame gap | 2 frames | Diagnose excessive missing frames |

![R5F INIT, FRESH, HOLD, and FAILSAFE state transitions driven by heartbeat and inference-result freshness](/assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/control-state-machine.svg)

**Freshness-Driven Control Policy.** The 10 ms task evaluates the latest value; the RPMsg callback never runs control logic. The default thresholds are 100 ms for heartbeat `HOLD`, 300 ms for heartbeat `FAILSAFE`, 200 ms for result `FAILSAFE`, and 500 ms for startup `FAILSAFE`. The maximum inference-latency diagnostic is 50 ms.

The receive callback only enters a short critical section and hands the packet to the decoder:

```cpp
taskENTER_CRITICAL();
(void)r5cd_policy_receive_packet(&control_policy, data, len, r5_time_us());
taskEXIT_CRITICAL();

/* Telemetry must not block the control loop. */
(void)rpmsg_trysend(ept, &response, sizeof(response));
```

`r5cd_apply_output()` is currently a weak no-op hook. This is intentional: communication and safety-state behavior can be verified without inventing an unsafe GPIO or PWM value. A product-specific implementation can later replace only this hook with the required deterministic output behavior.

## Auditing and Reserving Physical Memory

The default Vitis OpenAMP example used addresses near `0x3ED00000`. The target kernel was booted with `cma=1000M`, placing those example addresses inside memory that Linux could allocate. A remote processor may appear to start while still corrupting memory if its firmware, vrings, or buffers overlap CMA.

The live Device Tree, `/proc/iomem`, and kernel command line were audited before selecting a high DDR region beginning at `0x79000000`.

![Physical DDR reserved-memory layout for R5F firmware, trace, vrings, and RPMsg shared buffers](/assets/media/posts/r5f-freertos-a53-camera-dpu-integration/images/reserved-memory-map.svg)

**Boot-Time Reserved-Memory Contract.** Bar lengths are linearly proportional to the allocated size: 4 KiB for `RSC_TRACE`, 16 KiB for each vring, 256 KiB for the R5F firmware region, and 1 MiB for the RPMsg shared-buffer pool. The Device Tree, ELF program headers, resource table, linker script, and OpenAMP configuration must use the same physical addresses. The regions must be reserved before Linux allocates memory, remain outside CMA and other System RAM use, and never overlap one another. `RSC_TRACE` must avoid every firmware LOAD/BSS segment, and the RPMsg shared-buffer pool must begin at `0x79048000` rather than at either vring address. This layout was validated against the target's `cma=1000M` configuration.

The resulting contract is:

| Use | Start | Size | End |
|---|---:|---:|---:|
| R5F firmware DDR | `0x79000000` | `0x00040000` | `0x7903FFFF` |
| `RSC_TRACE` | `0x7903F000` | `0x00001000` | `0x7903FFFF` |
| vring0 | `0x79040000` | `0x00004000` | `0x79043FFF` |
| vring1 | `0x79044000` | `0x00004000` | `0x79047FFF` |
| RPMsg shared buffers | `0x79048000` | `0x00100000` | `0x79147FFF` |

`RSC_TRACE` occupies the last 4 KiB of the firmware reservation, but the linker and ELF checks guarantee that no LOAD or BSS segment uses that page. Without this separation, Linux trace handling could overwrite R5F static data.

The memory contract can be checked independently:

```bash
sw/r5f-camera-dpu/scripts/validate_memory_contract.sh
```

### Why the reservation must exist at boot

A `reserved-memory` overlay must not be added through configfs after Linux has booted. By that point the allocator may already own the physical pages. The implementation merges the overlay into the KV260 revB base DTB from the FIT image and installs it as `user-override.dtb`, allowing the boot loader to present the complete reservation to Linux from the beginning.

The overlay contains:

- the firmware, two vrings, and shared-buffer reserved-memory nodes;
- the R5F TCM nodes;
- the `xlnx,zynqmp-r5-remoteproc` node;
- the A53-to-R5F IPI mailboxes;
- the four `memory-region` references consumed by remoteproc.

Storage paths and physical addresses are different concerns:

- `/boot/firmware/user-override.dtb` is a file on the microSD boot partition;
- `/lib/firmware/r5f_camera_dpu_control.elf` is a file in the Ubuntu root filesystem;
- `0x79000000` and the other addresses identify physical DDR destinations at runtime.

The physical range must not overlap boot firmware, the Linux kernel or initrd, CMA, PL camera/DPU DMA buffers, another reserved-memory range, any R5F LOAD/BSS segment, `RSC_TRACE`, either vring, or the RPMsg buffer pool.

Useful target-side audit commands are:

```bash
cat /proc/cmdline
cat /proc/iomem
grep -E 'MemTotal|CmaTotal|CmaFree' /proc/meminfo
dtc -I fs -O dts /proc/device-tree > /tmp/live.dts
grep -nE '79000000|79040000|79044000|79048000' /tmp/live.dts
```

## Creating the Boot-Time Device Tree

The following commands run on the KV260. The existing override must be backed up before replacement.

```bash
cd ~/fpga_rtos_camera_ai

sudo cp -a /boot/firmware/user-override.dtb \
  /boot/firmware/user-override.dtb.backup-$(date +%Y%m%d-%H%M%S)

sw/r5f-camera-dpu/scripts/make_kv260_user_override.sh \
  /boot/firmware/image.fit /tmp/user-override.dtb

sudo install -m 0644 /tmp/user-override.dtb \
  /boot/firmware/user-override.dtb
sudo reboot
```

The helper extracts the sixth DTB from the FIT image and verifies that it describes `ZynqMP KV260 revB` before merging the overlay. This prevents an override from being built against the wrong board description.

After rebooting, verify the live nodes and the remoteproc instance:

```bash
find /proc/device-tree/reserved-memory -maxdepth 1 -mindepth 1 \
  -type d -printf '%f\n' | sort

find /sys/class/remoteproc -maxdepth 2 -type f -print
cat /sys/class/remoteproc/remoteproc0/state
cat /proc/cmdline
```

The following node names are required by the `linux-xlnx` 5.15 R5 remoteproc driver:

```text
rpu0vdev0vring0@79040000
rpu0vdev0vring1@79044000
rpu0vdev0buffer@79048000
```

These names are functional, not cosmetic. The driver identifies fixed vring and buffer carveouts by the `vdev0vring` and `vdev0buffer` substrings. Generic names can leave the reservation visible in the Device Tree while preventing it from being registered with the OpenAMP transport.

The R5F is not guaranteed to appear as `remoteproc0`. Read each instance's `name`, `firmware`, and `state`, then substitute the correct `remoteprocN` in later commands.

## Building the R5F Firmware with Vitis 2024.2

The build host requires Vitis 2024.2 and the XSA exported from the camera/DPU design. The default SmartCam-derived XSA is:

Vitis embedded-software projects were traditionally created and configured mainly through the Vitis GUI. That interactive workflow remains useful for inspecting a platform, but current AI coding agents can help analyze the generated artifacts, construct Tcl and shell automation, and iterate on build failures directly from the command line. Because the same objective can now be reached through a traceable and repeatable CLI-based workflow, this article records the command-line procedure rather than a sequence of GUI operations.

```text
sw/camera-dpu/kria-vitis-platforms/kv260/overlays/examples/smartcam/
  binary_container_1/link/int/vpl_gen_fixed.xsa
```

Build the firmware into a new workspace:

```bash
cd /path/to/fpga_rtos_camera_ai

sw/r5f-camera-dpu/scripts/build_vitis_control.sh \
  sw/camera-dpu/kria-vitis-platforms/kv260/overlays/examples/smartcam/\
binary_container_1/link/int/vpl_gen_fixed.xsa \
  /tmp/r5f-camera-dpu-control-build
```

If Vitis is installed elsewhere, specify its settings script:

```bash
VITIS_SETTINGS=/tools/Xilinx/Vitis/2024.2/settings64.sh \
  sw/r5f-camera-dpu/scripts/build_vitis_control.sh <xsa> <new-workspace>
```

A successful build installs these artifacts under `sw/r5f-camera-dpu/firmware`:

```text
r5f_camera_dpu_control.elf
r5f_camera_dpu_control.map
MEMORY_CONTRACT
SHA256SUMS
```

### What the build automates

The Vitis Tcl flow:

1. Creates a `psu_cortexr5_0` platform from the XSA.
2. Creates a `freertos10_xilinx` domain.
3. Adds `xiltimer`, `libmetal`, and `openamp` to the BSP.
4. Enables `WITH_RPMSG_USERSPACE=true`.
5. Generates the Vitis OpenAMP echo-test template.
6. Replaces the example application with the project control and policy sources.
7. Patches the linker script, resource table, and platform glue for the audited KV260 contract.
8. Produces the ELF, map, checksum, and memory-contract files.

Using the vendor template retains resource-table and libmetal glue that matches the installed BSP. However, the Vitis 2024.2 template needed several target-specific corrections:

- move firmware, vrings, shared buffers, and trace to the audited addresses;
- place `.ARM.exidx` in DDR to avoid an `R_ARM_PREL31` relocation-distance overflow;
- compile the mixed C and C++ project with the correct compilers;
- fix an invalid free of an interior `rpmsg_virtio_device` pointer;
- convert the physical IPI IRQ number into the FreeRTOS local-vector representation;
- install the OpenAMP handler into the scheduler-owned GIC without reinitializing it;
- collect an IPI that arrived before handler registration.

The patch script verifies the exact number of expected template strings before changing them. If a future Vitis release changes the template, the build stops instead of silently producing firmware from an unreviewed patch.

### Verifying the ELF before deployment

```bash
cd /path/to/fpga_rtos_camera_ai/sw/r5f-camera-dpu
(cd firmware && sha256sum -c SHA256SUMS)
scripts/verify_r5_elf.sh firmware/r5f_camera_dpu_control.elf
```

The verifier checks the ARM machine type, resource-table placement, vring addresses and descriptor counts, trace address and size, all LOAD/BSS ranges, and every possible overlap among firmware, trace, vrings, and shared buffers.

The Device Tree and ELF are two sides of the same physical-memory contract. Updating only one of them is unsafe.

## Deploying and Starting the R5F

In this design, deploying the R5F firmware does not mean writing a flat binary directly to a physical flash address. The verified ELF is stored under `/lib/firmware`; at each start, Linux remoteproc parses its program headers and resource table, copies each segment into the correct TCM or reserved DDR location, creates virtio resources, and releases the R5F.

Install the ELF on the KV260:

```bash
cd ~/fpga_rtos_camera_ai
sudo install -m 0644 \
  sw/r5f-camera-dpu/firmware/r5f_camera_dpu_control.elf \
  /lib/firmware/r5f_camera_dpu_control.elf
```

Start it through the correct remoteproc instance:

```bash
cat /sys/class/remoteproc/remoteproc0/state

echo r5f_camera_dpu_control.elf | \
  sudo tee /sys/class/remoteproc/remoteproc0/firmware
echo start | sudo tee /sys/class/remoteproc/remoteproc0/state

cat /sys/class/remoteproc/remoteproc0/state
dmesg | tail -n 100
```

Success requires a `running` state with no carveout or remoteproc crash. If remoteproc debugfs is mounted, inspect the R5 trace as well:

```bash
sudo cat /sys/kernel/debug/remoteproc/remoteproc0/trace0 | strings
```

The expected initialization has this form:

```text
IPI ready: metal vector=33 GIC IRQ=65 enable=0x12 pending=0
R5CD endpoint ready: rpmsg-openamp-demo-channel
```

The exact enable value may contain unrelated bits. The important evidence is that local vector 33 maps to physical GIC IRQ 65, the corresponding enable bit is set, the RPMsg name service appears, and real packets can travel in both directions.

## Creating the Linux RPMsg Endpoint

When the R5F advertises `rpmsg-openamp-demo-channel`, Linux creates an RPMsg control device. Read the service name and destination address from sysfs rather than assuming an address:

```bash
for d in /sys/bus/rpmsg/devices/*; do
  test -e "$d/name" || continue
  printf '%s name=%s src=%s dst=%s\n' "$d" \
    "$(cat "$d/name")" "$(cat "$d/src")" "$(cat "$d/dst")"
done
```

The verified target used destination address `1024`. Build the A53 utilities and create an `rpmsg-char` endpoint:

```bash
make -C sw/r5f-camera-dpu a53-cross

sudo sw/r5f-camera-dpu/build/r5cd-eptctl-aarch64 create \
  /dev/rpmsg_ctrl0 rpmsg-openamp-demo-channel 1024 0
```

The utility issues `RPMSG_CREATE_EPT_IOCTL`, waits for the corresponding sysfs entry, and prints the generated `/dev/rpmsgN` path. Use that exact device for the following tests.

## Testing RPMsg Before the Camera Pipeline

First send 20 synthetic results at 20 ms intervals, each valid for 50 ms:

```bash
sudo sw/r5f-camera-dpu/build/r5cd-test-client-aarch64 \
  /dev/rpmsg0 20 20 0 50
```

The applied sequence should advance and the R5F should enter `FRESH`. The output follows this format:

```text
status applied=<increasing sequence> state=1 age_us=<less than 50000> \
faults=0x00000000 dropped=0 overwritten=<value> \
deadline_misses=0 max_late_us=0
```

Next, mark the same results as already 100 ms old when sent:

```bash
sudo sw/r5f-camera-dpu/build/r5cd-test-client-aarch64 \
  /dev/rpmsg0 20 20 100 50
```

The 100 ms source age exceeds the 50 ms validity interval. The applied sequence must not advance, while the drop count and `R5CD_FAULT_RESULT_EXPIRED` fault increase:

```text
status applied=0 state=<INIT or FAILSAFE> age_us=4294967295 \
faults=0x00000002 dropped=<increasing value> overwritten=0 \
deadline_misses=<value> max_late_us=<value>
```

Additional transport tests should include:

- restarting the A53 client and accepting sequence one under a new `sender_instance`;
- stopping heartbeats and observing `HOLD` after 100 ms and `FAILSAFE` after 300 ms;
- destroying the endpoint and stopping/starting remoteproc at least ten times;
- confirming that `dmesg` contains neither `Failed to kick remote` nor `MBOX_TX_QUEUE_LEN` failures.

Stop the standalone test cleanly:

```bash
sudo sw/r5f-camera-dpu/build/r5cd-eptctl-aarch64 destroy /dev/rpmsg0
echo stop | sudo tee /sys/class/remoteproc/remoteproc0/state
```

## Integrating the Camera and DPU Publisher

Only after standalone transport became stable was the publisher added to the real A53 pipeline. The application uses two tensor slots so that DPU execution for frame N can overlap camera capture and preprocessing for frame N+1.

When a slot finishes, the sequence is:

1. Wait for the DPU job.
2. Run face-detection postprocessing.
3. Convert detections into the common message format.
4. Publish a heartbeat and vision result.
5. Drain available `CONTROL_STATUS` packets without blocking.

The integration point is equivalent to:

```cpp
const uint64_t publish_start_ns = monotonic_ns();
(void)r5cd_publish_heartbeat(publisher, publish_start_ns, 0U);
(void)r5cd_publish_vision(publisher, &result, publish_start_ns);
```

The publisher opens the RPMsg character device with `O_NONBLOCK`. Each vision packet carries the camera capture timestamp, DPU completion timestamp, frame sequence, validity period, and source age calculated immediately before transmission. The R5F therefore evaluates total age from camera capture, not merely time spent inside RPMsg.

The current capture path maps DMA-backed NV12 planes from V4L2 and reads them directly during preprocessing. The A53 implementation can evolve from the original GStreamer/VVAS flow without changing the R5F boundary, because the R5F consumes only the fixed-size post-inference result.

## Integrating R5F Startup into the Camera Launcher

The camera launcher performs these operations in order:

1. Unload the current FPGA application and load `kv260-raspi-dpu` with `xmutil`.
2. Stop and restart the R5F remoteproc after the FPGA application is loaded.
3. Wait for the RPMsg control channel.
4. Destroy any stale endpoint and create a new one for the advertised destination.
5. Configure the camera and ISP gain.
6. Prepare the application runtime environment.
7. Pass the new `/dev/rpmsgN` device to the A53 camera/DPU process.

Recreating the endpoint after `xmutil loadapp` is important. Reusing an RPMsg endpoint across a PL application change can leave the camera operational while the publisher points at a stale character device.

The principal launcher settings are:

| Variable | Default | Purpose |
|---|---|---|
| `R5CD_MANAGE_R5F` | `1` | Let the camera launcher manage remoteproc |
| `R5CD_REMOTE_PROC` | `/sys/class/remoteproc/remoteproc0` | R5F remoteproc path |
| `R5CD_FIRMWARE_NAME` | `r5f_camera_dpu_control.elf` | ELF name under `/lib/firmware` |
| `R5CD_RPMSG_CONTROL_DEVICE` | `/dev/rpmsg_ctrl0` | RPMsg control device |
| `R5CD_RPMSG_SERVICE` | `rpmsg-openamp-demo-channel` | Name-service channel |
| `R5CD_RPMSG_DESTINATION` | `1024` | R5F endpoint address |
| `R5CD_USE_RPMSG` | `1` | Enable R5F integration in the A53 pipeline |

## Complete Build and Run Flow

The target must already have the boot-time DTB, verified R5F ELF under `/lib/firmware`, FPGA application, model, camera, and DisplayPort output.

To build natively and run on the KV260:

```bash
cd ~/fpga_rtos_camera_ai/sw/r5f-camera-dpu
scripts/build_and_run_camera.sh
```

To cross-build from another Linux host, copy the result, and run it remotely:

```bash
cd /path/to/fpga_rtos_camera_ai/sw/r5f-camera-dpu
KV260_HOST=ubuntu@<kv260-address> scripts/build_and_run_camera.sh
```

Use `--build-only` to stop after compilation:

```bash
scripts/build_and_run_camera.sh --build-only
```

Use `--monitor` to save A53 pipeline timing as CSV and SVG:

```bash
scripts/build_and_run_camera.sh --monitor
```

The A53 monitor records camera/ISP-to-userspace wait, dequeue, map, preprocessing, DPU, postprocessing, and RPMsg publication. R5F control-task deadline misses come from `CONTROL_STATUS`. Keeping the two measurements separate avoids confusing Linux camera-pipeline jitter with real-time control-task lateness.

## Bring-Up Failures and Root Causes

### Remoteproc runs, but no name service appears

The kernel reported:

```text
Allocated carveout doesn't fit device address request
```

The original reserved-memory nodes had generic names such as `r5cd-vring0`. The `linux-xlnx` 5.15 driver did not identify them as fixed OpenAMP carveouts and attempted to allocate different memory from CMA. Renaming them to `rpu0vdev0vring0`, `rpu0vdev0vring1`, and `rpu0vdev0buffer` fixed the mapping. Both the boot DTB and ELF must be regenerated when this contract changes.

### The name service appears, but A53 writes time out

The OpenAMP shared-buffer pool was incorrectly placed at the vring0 address. A vring descriptor region is not the data-buffer pool. The correct separation is:

```text
vring0      = 0x79040000
vring1      = 0x79044000
buffer pool = 0x79048000
```

The memory-contract validator now rejects overlap and confirms the generated platform header contains the proper buffer base.

### A53 kicks arrive, but the R5F does not process them

Mailbox routing was active, but physical GIC IRQ 65 was not enabled. The Vitis template passed physical ID 65 into a FreeRTOS wrapper that adds the SPI offset of 32, attaching the handler to IRQ 97 instead. The firmware now converts the interrupt to local vector `65 - 32 = 33`.

The communication task must also avoid reinitializing the GIC after FreeRTOS owns it, because doing so removes the scheduler tick and existing handlers. The OpenAMP callback is installed into the existing controller with `xPortInstallInterruptHandler()`.

### The first kick is lost

Linux can notify the R5F before its handler is registered. Initialization now reads the IPI pending state, clears the relevant bit, and lets the OpenAMP poll loop process the pending event.

### `rpmsg-char` writes fail temporarily

A nonblocking character device may return `EAGAIN` while a vring is unavailable. The A53 publisher retries at 1 ms intervals for up to 2000 attempts. Retries are not a substitute for correcting a persistent node-name, buffer-address, or interrupt problem.

### The camera works, but the integrated launcher does not communicate

The endpoint may have been created before `xmutil loadapp` and then reused. The launcher must restart remoteproc and recreate the RPMsg endpoint after loading the FPGA application, then pass the newly resolved `/dev/rpmsgN` to the A53 process.

## Verification Checklist

### Host and firmware

- `make -C sw/r5f-camera-dpu check` passes.
- The R5F ELF can be reproduced from the XSA with Vitis 2024.2.
- `verify_r5_elf.sh` passes.
- The ELF, Device Tree, resource table, linker script, and `MEMORY_CONTRACT` use identical addresses.

### KV260 after boot

- The live Device Tree contains all three `rpu0vdev0...` nodes.
- Firmware, vrings, and shared buffers do not overlap CMA or another consumer.
- The correct remoteproc instance has been identified.
- The R5F reaches `running` without a carveout error.
- The trace reports local vector 33 and physical IRQ 65.
- `rpmsg-openamp-demo-channel` appears through the name service.
- An `/dev/rpmsgN` endpoint can be created.

### Transport and policy

- A fresh synthetic result enters `FRESH` and advances the applied sequence.
- A stale-at-send result is rejected with `R5CD_FAULT_RESULT_EXPIRED`.
- A heartbeat timeout causes `HOLD`, followed by `FAILSAFE`.
- A new `sender_instance` is accepted after the A53 publisher restarts.
- Repeated remoteproc and endpoint restart cycles recover cleanly.
- The kernel log contains no persistent remote-kick or mailbox-queue errors.

### Camera integration

- Camera, ISP, DPU, and display continue to run while the R5F is active.
- Real frame sequences and capture timestamps reach the R5F.
- Linux receives and displays control state, faults, drops, and deadline telemetry.
- Stopping the camera application causes the R5F to enter `HOLD` and then `FAILSAFE`.
- A53 pipeline latency and R5F deadline behavior are recorded as separate measurements.

## Conclusion

Adding the Cortex-R5F to the KV260 camera system required more than writing a FreeRTOS task. The working implementation depends on a consistent contract across the boot-time Device Tree, ELF program headers, linker script, OpenAMP resource table, Linux remoteproc driver, shared-buffer pool, and IPI interrupt mapping.

The key architectural choice is equally important: the A53 retains the complex Linux camera and DPU environment, while the R5F receives only fixed-size, timestamped results through a latest-value mailbox. This permits camera-pipeline jitter on Ubuntu without allowing an old inference result or a stalled Linux process to control an actuator indefinitely.

By validating memory, firmware loading, interrupts, RPMsg transport, freshness policy, and camera integration as separate gates, the original camera-only design was extended into a heterogeneous multi-core system without destabilizing its image path. The remaining board-specific step is to replace the no-op output hook with the required GPIO, PWM, motor, or servo behavior and verify the physical safe state under injected faults.
