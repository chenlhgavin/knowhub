# ComfyUI + InfiniteTalk AutoDL 部署步骤

## 前置条件

- AutoDL 镜像：**PyTorch 2.8.0 / Python 3.12 (ubuntu22.04) / CUDA 12.8**
- GPU：推荐 RTX 5090 (32GB)；RTX 4090 (24GB) 亦可（需调高 block_swap）
- 硬盘：数据盘建议 **150GB+**（模型文件较大）
- 开始前确保 **GPU 已开启**（非无卡模式），SageAttention 编译需要 GPU

---

## 第一步：安装 ComfyUI 核心

AutoDL 镜像已自带 Python 3.12 和 PyTorch，无需创建 conda 环境。

```bash
cd /root

# 克隆 ComfyUI
git clone https://ghfast.top/github.com/Comfy-Org/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# 安装额外依赖
pip install color-matcher imageio-ffmpeg
```

---

## 第二步：安装加速组件

### 2.1 flash-attn

AutoDL 已预装 triton，只需装 flash-attn：

```bash
pip install flash-attn --no-build-isolation
```

### 2.2 源码编译 SageAttention

> 此步骤需要 GPU，确认 AutoDL 实例已开启 GPU。

```bash
cd /root
git clone https://ghfast.top/github.com/thu-ml/SageAttention.git
cd SageAttention
python setup.py install
```

验证安装：

```bash
python -c "import sageattention; print('SageAttention OK')"
```

---

## 第三步：安装自定义节点

```bash
cd /root/ComfyUI/custom_nodes/

# [核心] WanVideo 适配器
git clone https://ghfast.top/github.com/kijai/ComfyUI-WanVideoWrapper.git
cd ComfyUI-WanVideoWrapper && pip install -r requirements.txt && cd ..

# [核心] 语音驱动
git clone https://ghfast.top/github.com/christian-byrne/audio-separation-nodes-comfyui.git

# [必备] 视频处理与增强工具
git clone https://ghfast.top/github.com/ltdrdata/ComfyUI-Impact-Pack.git
git clone https://ghfast.top/github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
git clone https://ghfast.top/github.com/kijai/ComfyUI-KJNodes.git
git clone https://ghfast.top/github.com/yolain/ComfyUI-Easy-Use.git
git clone https://ghfast.top/github.com/rgthree/rgthree-comfy.git
```

---

## 第四步：准备模型目录

将 models 目录移到数据盘，避免系统盘空间不足：

```bash
cd /root/ComfyUI
mv models /root/autodl-tmp/
ln -s /root/autodl-tmp/models ./models
```

---

## 第五步：安装 hfd 下载工具

```bash
wget https://hf-mirror.com/hfd/hfd.sh -O /usr/local/bin/hfd.sh
chmod +x /usr/local/bin/hfd.sh

# 设置 HF-Mirror 环境变量（AutoDL 国内网络必需）
export HF_ENDPOINT=https://hf-mirror.com
```

> 建议将 `export HF_ENDPOINT=https://hf-mirror.com` 写入 `~/.bashrc` 以持久化。

---

## 第六步：下载模型权重

### 6.1 扩散模型

```bash
# Wan2.1 基础模型 (FP8, ~14GB)
hfd.sh Kijai/WanVideo_comfy_fp8_scaled \
  --include Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors \
  --local-dir /root/autodl-tmp/models/diffusion_models

# InfiniteTalk 微调权重
mkdir -p /root/autodl-tmp/models/diffusion_models/InfiniteTalk
hfd.sh Kijai/WanVideo_comfy \
  --include Wan2_1-InfiniTetalk-Single_fp16.safetensors \
  --local-dir /root/autodl-tmp/models/diffusion_models/InfiniteTalk/
```

### 6.2 文本与视觉编码器

```bash
# T5 文本编码器
hfd.sh Kijai/WanVideo_comfy \
  --include umt5-xxl-enc-bf16.safetensors \
  --local-dir /root/autodl-tmp/models/text_encoders

# CLIP 视觉编码器
mkdir -p /root/autodl-tmp/models/clip_vision
hfd.sh Kijai/CLIPVisionModelWithProjection_fp16 \
  --include CLIP-ViT-H-fp16.safetensors \
  --local-dir /root/autodl-tmp/models/clip_vision
```

### 6.3 音频编码器

```bash
hfd.sh TencentGameMate/chinese-wav2vec2-base \
  --local-dir /root/autodl-tmp/models/transformers/TencentGameMate/chinese-wav2vec2-base
```

### 6.4 VAE 与 LoRA

```bash
# VAE
hfd.sh Kijai/WanVideo_comfy \
  --include Wan2_1_VAE_bf16.safetensors \
  --local-dir /root/autodl-tmp/models/vae

# Distill LoRA（4步加速）
hfd.sh Kijai/WanVideo_comfy \
  --include lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors \
  --local-dir /root/autodl-tmp/models/loras
```

---

## 第七步：验证模型文件

运行以下命令确认所有文件就位：

```bash
echo "=== 扩散模型 ==="
ls -lh /root/autodl-tmp/models/diffusion_models/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors
ls -lh /root/autodl-tmp/models/diffusion_models/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors

echo "=== 文本编码器 ==="
ls -lh /root/autodl-tmp/models/text_encoders/umt5-xxl-enc-bf16.safetensors

echo "=== CLIP 视觉 ==="
ls -lh /root/autodl-tmp/models/clip_vision/CLIP-ViT-H-fp16.safetensors

echo "=== Wav2Vec ==="
ls /root/autodl-tmp/models/transformers/TencentGameMate/chinese-wav2vec2-base/

echo "=== VAE ==="
ls -lh /root/autodl-tmp/models/vae/Wan2_1_VAE_bf16.safetensors

echo "=== LoRA ==="
ls -lh /root/autodl-tmp/models/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors

echo "=== 软链接 ==="
ls -la /root/ComfyUI/models
```

---

## 第八步：启动 ComfyUI

```bash
cd /root/ComfyUI
python main.py --port=6006 --listen=0.0.0.0 --enable-manager
```

AutoDL 端口映射参考：https://www.autodl.com/docs/port/

---

## 第九步：加载工作流

1. 浏览器通过 AutoDL 代理地址访问 ComfyUI 界面
2. 将 `infinitetalk单人 (4).json` 工作流文件拖入界面加载
3. 上传参考人脸图片和音频素材到 ComfyUI 的 input 目录
4. 点击 **Queue Prompt** 开始生成

---

## 注意事项

### 首次运行

torch_compile 首次运行会进行内核编译，后台会卡住约 5-8 分钟，属正常现象，请勿关闭。后续运行恢复正常速度。

### 显存调优

在另一个终端运行 `watch -n 1 nvidia-smi` 监控显存：

| GPU | block_swap 建议值 |
|---|---|
| RTX 5090 (32GB) | 0 或 5（速度更快） |
| RTX 4090 (24GB) | 20~30（防止 OOM） |

如果显存溢出，在工作流 Node 134 中调高 `blocks_to_swap` 值。

### API 调用

如需通过脚本远程提交任务，使用 API 格式的工作流文件 `infinitetalk单人 (3).json`，通过 `/prompt` 接口提交，通过 `/history/{prompt_id}` 获取结果。详见原始文档第八章。
