---
layout: post
title: SAM2 Video Segmentation inference on Jetson Orin Nano 
date: 2025-08-24
author: Ryoga Yuzawa
categories: [AI, Computer Vision, Jetson, Docker, SAM2]
tags: [Jetson Orin Nano, SAM2, Docker, VSCode, Computer Vision, AI, Environment Setup]
image: /assets/images/sam2-video-predictor.png
description: "Jetson Orin Nano SuperでSAM2（Segment Anything Model 2）の環境を構築し、DockerコンテナとVSCodeを連携させて効率的な開発環境を作る方法を解説します。"
keywords: "Jetson Orin Nano, SAM2, Docker, VSCode, Computer Vision, AI, Environment Setup, Jetson"
---

## はじめに
Jetson Orin Nano上でSAM2 動画推論を動かしたときのメモ

## 環境仕様

### ハードウェア・ソフトウェア構成
- **Board**: Jetson Orin Nano Super
- **FW**: Jetpack 6.2
- **OS**: Ubuntu 22.04
- **CUDA Toolkit**: 12.6
- **cuDNN**: 12.6
- **Python**: 3.10

## Jetson向けPyTorch+Transformer環境コンテナ作成

### 1. 基本セットアップ
```bash
git clone https://github.com/dusty-nv/jetson-containers.git
bash jetson-containers/install.sh
CUDA_VERSION=12.6 jetson-containers build l4t-ml transformers
```

- l4t-ml (pytorch+etc) + transformers環境を作る

### 2. NCCLビルド時のメモリ不足対策
NCCLビルド時にOut of memoryで落ちてしまった場合の対処法：

**対象ファイル**: `packages/cuda/nccl/build.sh`

**修正内容**:

```bash
make -j2 src.build NVCC_GENCODE="-gencode=arch=compute_87,code=sm_87"
make -j2 pkg.txz.build NVCC_GENCODE="-gencode=arch=compute_87,code=sm_87"
```

- job数を2に制限することで、メモリ使用量を抑制
- ビルドには約8時間を要する

### 3. コンテナの起動と確認

```bash
jetson-containers run --volume /ssd/work:/work --workdir /work $(autotag l4t-ptx-transformers)
```

- 自分は上記イメージをl4t-ptx-transformersとして作った

**環境確認**:
```bash
pip list
```

- 一通りpytorchやtransformerなど入っていればビルドOK
- `nvidia-smi`などして出てくればOK, JetsonはSoCとしてGPUがあるのでN/Aとなる
- 途中でfailしている場合もコンテナ内に入れてしまうので、その場合は各種ライブラリが無い

## SAM2 Install

### 1. リポジトリのクローン
```bash
jetson-containers run --volume /ssd/work:/work --workdir /work $(autotag l4t-ptx-transformers)
git clone https://github.com/facebookresearch/sam2
```

### 2. セットアップ
- あとは公式のリポジトリに従ってcheckpointなどインストール
- Jetsonだとlarge系はメモリが怪しいので軽量モデルに変更
- もしかしたら動画ロード時にOOMになってKernelクラッシュするので、その際はメモリ最適化を行う
   - ここの手順にそって進めればOK
      https://bone.jp/articles/2025/250125_JetsonOrinNanoSuper_4_memory

**軽量モデルの設定**:
```python
sam2_checkpoint = "../checkpoints/sam2.1_hiera_tiny.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_t.yaml"
```

## Docker環境でのipynb実行

VSCodeで実行していく。前提条件としてDev Container, Docker, JupyterのExtensionが必要

### 1. Jupyter環境のセットアップ
```bash
jetson-containers run --volume /ssd/work:/work --workdir /work $(autotag l4t-ptx-transformers)
pip install jupyterlab ipykernel
python -m ipykernel install --user --name jetson-docker
```

### 2. VSCodeでのコンテナ接続
1. `Ctrl + Shift + P` → `Dev Containers: Attach to Running Container`
2. 今動いているl4t-ptx-transformersを選択
3. 新しいウィンドウが立ち上がる。左下にContainer jetson_contaner…と表示されてればOK

### 3. 作業ディレクトリの設定
1. `File` → `Open Folder` → `/work`
2. **注意**: workは直打ちしないとsuggestに出てこないので注意。地味にハマリどころ
3. これでContainer環境でipynbノートブックがVSCode上で開ける

## SAM2 Video predictor 実行

### 1. ノートブックの準備
```bash
cd ./sam2/notebooks
```

- GUIでvideo_predictor_exmple.ipynbを開く

### 2. カーネルの選択
- 右上のSelect Kernel → Jupyter Kernel → jetson-docker
- ない場合はVSCode再起動するとだいたい出てくる

### 3. 実行とトラブルシューティング
- 後は普通に実行するとＯＫ
- l4t-ml + transformer コンテナ環境だと下記でハマった

**よくある問題と対処法**:

1. **opencv, matplotlibがない**
   ```bash
   pip install opencv-python matplotlib
   ```

2. **numpy is not availableエラー**
   - pip側 numpy verのエラーみたい。pip側numpyを1.26にしたらいけた
   ```bash
   pip uninstall numpy
   python3 -m pip install -U pip
   ```
   - Restart Kernel

### 4. 実行結果
動いた

![SAM2 Video Predictor実行結果](/assets/images/sam2-video-predictor.png)

## GPUリソースの確認

### tegrastatsによる監視
- GPU使用してるかどうかは`tegrastats`で確認できる
- GR3D_FREQがJetson OrinのGPUリソース消費
- `predictor.propagate_in_video`実行中に`tegrastats`で確認し、GPUリソースが増加していればGPU上でSAM2を処理できている

**実行例**:

```
[2%@1728,44%@1728,4%@1728,30%@1728,4%@729,3%@729] **GR3D_FREQ 99%** cpu@54.468C soc2@52.687C soc0@53.406C gpu@55.093C tj@55.093C soc1@52.718C VDD_IN 18426mW/7206mW VDD_CPU_GPU_CV 7601mW/922mW VDD_SOC 5651mW/3175mW
08-24-2025 17:49:08 RAM 7124/7620MB (lfb 1x1MB) SWAP 3906/20194MB (cached 159MB) CPU 
```

→ 99%になっている

## その他

- 本Docker環境を使うことでそのままSLM(llama-3 on hugging face)なども普通に実行できた