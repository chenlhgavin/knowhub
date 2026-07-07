ComfyUI部署

**一、 项目组成架构**

在开始部署前，必须理解本实验涉及的五个核心技术板块：

**生成引擎 (Base Engine):** **Wan2.1-14B**。阿里巴巴开源的最先进视频大模型，负责生成高动态、高质感的视频底稿。

**驱动核心 (Driving Core):** **InfiniteTalk**。基于 Wan2.1 的微调模型，专门用于实现超长、高保真的数字人面部驱动与口型同步。

**理解模块 (Perception):**

**T5 (umt5-xxl):** 强大的文本理解器，处理提示词。

**CLIP Vision:** 视觉编码器，提取参考图的人物特征。

**Wav2Vec2:** 音频编码器，将语音信号转化为面部运动潜空间向量。

> **常见疑问：CLIP 能否替代 T5 处理文本提示词？**
>
> 不能。虽然 CLIP 同时具备文本编码器和视觉编码器，但本管线中仅使用其 **Vision 编码器**提取参考图的人脸视觉特征，并未使用其文本端。两者的核心差异如下：
>
> | | **CLIP（文本编码器）** | **T5 (umt5-xxl)** |
> |---|---|---|
> | **训练方式** | 对比学习——学习文本与图像的匹配关系 | 自监督文本生成——大规模语料上的深度语言理解 |
> | **文本理解深度** | 浅层，偏向关键词级别的视觉概念映射 | 深层，能处理从句、修饰关系、抽象描述 |
> | **参数量级** | 文本端约 ~340M | umt5-xxl 约 **13B**，相差一个数量级 |
> | **典型局限** | 长句理解差、易忽略修饰词、对词序不敏感 | 无此局限，擅长复杂语义解析 |
>
> 以提示词 `"一个穿着职业装的女性在办公室开心地说话，背景模糊"` 为例，T5 能准确拆解"职业装→服装风格、办公室→场景环境、开心地说话→表情动作、背景模糊→景深效果"等多层语义关系，而 CLIP 文本端难以可靠地区分这些修饰层次。这也是 Wan2.1 等新一代视频模型选用 T5 而非 CLIP 做文本编码的原因。
>
> 简单类比三个编码器的分工：**CLIP Vision** 是看照片的"眼睛"（识别人物外貌），**T5** 是读剧本的"大脑"（理解场景描述），**Wav2Vec2** 是听声音的"耳朵"（解析语音节奏）。三者各有感知通道，不可互换。

**加速矩阵 (Acceleration Stack):**

**SageAttention:** 核心算子优化，解决长视频生成的显存爆炸问题。

**4-Step Distill LoRA:** 蒸馏技术，将 50 步的生成过程压缩至 4 步。

**Block Swap & Torch Compile:** 显存动态调度与静态图编译加速。

**辅助系统 (Auxiliary):** 包括面部重绘（Impact Pack）、视频合成（VHS）等，用于提升最终产出质量。

**二、 环境准备**

**显卡和Python、Torch、Cuda 版本**

<img src="media/image1.png" style="width:5.75in;height:4.25in" />

镜像 PyTorch 2.8.0  Python 3.12(ubuntu22.04) CUDA 12.8
GPU RTX 5090(32GB)

CPU 25 vCPU Intel(R) Xeon(R) Platinum 8470Q

内存90G
硬盘 系统盘：30GB 数据盘  50GB+100GB SSD



**Github加速**

在gitclone前加上下面的前缀可自动使用代理加速github代码拉取：

ghfast.top/

下面的代码已自动加上，如不需要可自行去除哈~

**1. 基础环境构建**

创建 Python 3.12 环境（针对大模型优化的版本）  
使用auodl镜像的同学就不用再创建conda环境了，下面2个命令可略过

conda create -n comfyui python=3.11 -y
conda activate comfyui



安装ComfyUI和一些其他依赖

# 安装 ComfyUI 核心<br />
git clone https://ghfast.top/github.com/Comfy-Org/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# 这里需要安装一些额外的库来保证工作流运行成功
pip install color-matcher
pip install imageio-ffmpeg
# 如果提示有些包找不到，可以切其他pip的源测试


**2. 核心加速组件安装 (重点)**

**SageAttention** 是 Wan2.1 能够顺畅运行的灵魂。根据历史记录，建议采用源码编译方式以获得最佳兼容性。

# 安装基础加速库
# autodl的同学可以略过triton，因为默认是已经安装了的
pip install triton flash-attn --no-build-isolation

# 源码编译安装 SageAttention
git clone https://ghfast.top/github.com/thu-ml/SageAttention.git
cd SageAttention
# 到这一步的时，此时使用AutoDL无卡模式的的同学记得要把GPU打开了哦，不然下面一步无法成功。
python setup.py install
# 验证安装
python -c "import sageattention; print('SageAttention Success')"



**三、 自定义节点部署**

进入 ComfyUI/custom_nodes 目录，安装工作流所需的模型：

```bash
cd ~/ComfyUI/custom_nodes/

# [核心] WanVideo 适配器
git clone https://ghfast.top/github.com/kijai/ComfyUI-WanVideoWrapper.git
cd ComfyUI-WanVideoWrapper && pip install -r requirements.txt && cd ..

# [核心] 语音驱动与多模型加载
git clone https://ghfast.top/github.com/christian-byrne/audio-separation-nodes-comfyui.git
# 注：此处对应 JSON 中的 MultiTalk 节点系列

# [必备] 视频处理与增强工具
git clone https://ghfast.top/github.com/ltdrdata/ComfyUI-Impact-Pack.git # 面部修复
git clone https://ghfast.top/github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git # 视频合成
git clone https://ghfast.top/github.com/kijai/ComfyUI-KJNodes.git # 图像缩放
git clone https://ghfast.top/github.com/yolain/ComfyUI-Easy-Use.git # 流程简化
git clone https://ghfast.top/github.com/rgthree/rgthree-comfy.git # 节点管理
```

**四、 模型下载**

**推荐：使用HF-Mirror的hfd工具进行模型下载，安装参考**

https://hf-mirror.com/

为了方便使用，可以把hfd.sh移动到/usr/local/bin目录下\`\`

```
mv hfd.sh /usr/local/bin/
```

**推荐：将ComfyUI的models目录软连接到autodl数据盘**

在 AutoDL 环境中，由于系统盘（/）空间较小，而数据盘（/root/autodl-tmp）空间较大，且可以扩容，所以将模型路径修改到数据盘是推荐做法。

```
# 假设你在 ComfyUI 根目录下
mv models /root/autodl-tmp/
ln -s /root/autodl-tmp/models ./models
```

接下来，按照 JSON 工作流定义的路径，严格放置权重文件。

**1. 扩散模型与微调权重**

**基础模型 (FP8)**: models/diffusion_models/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors

https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/blob/main/I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors

```
hfd.sh Kijai/WanVideo_comfy_fp8_scaled \
--include Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors \
--local-dir /root/autodl-tmp/models/diffusion_models
```

**InfiniteTalk 权重**: models/diffusion_models/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors

https://huggingface.co/Kijai/WanVideo_comfy/blob/main/InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors

*(对应 JSON 节点 212)*

```
hfd.sh Kijai/WanVideo_comfy \
--include Wan2_1-InfiniTetalk-Single_fp16.safetensors \
--local-dir /root/autodl-tmp/models/diffusion_models/InfiniteTalk/
```

**2. 文本与视觉理解模型**

**T5 编码器**: models/text_encoders/umt5-xxl-enc-bf16.safetensors

https://huggingface.co/Kijai/WanVideo_comfy/blob/main/umt5-xxl-enc-bf16.safetensors

```
hfd.sh Kijai/WanVideo_comfy \
--include umt5-xxl-enc-bf16.safetensors \
--local-dir /root/autodl-tmp/models/text_encoders
```

**CLIP 视觉**: models/clip/CLIP-ViT-H-fp16.safetensors

https://huggingface.co/Kijai/CLIPVisionModelWithProjection_fp16/blob/main/CLIP-ViT-H-fp16.safetensors

```
hfd.sh Kijai/CLIPVisionModelWithProjection_fp16 \
--include CLIP-ViT-H-fp16.safetensors \
--local-dir /root/autodl-tmp/models/clip_vision
```

**Wav2Vec**: 自动下载或手动放入 models/transformers/TencentGameMate/chinese-wav2vec2-base

> https://huggingface.co/TencentGameMate/chinese-wav2vec2-base

```
hfd.sh TencentGameMate/chinese-wav2vec2-base \
--local-dir /root/autodl-tmp/models/transformers/TencentGameMate/chinese-wav2vec2-base
```

**3. VAE 与 LoRA**

**VAE**: models/vae/Wan2_1_VAE_bf16.safetensors

https://huggingface.co/Kijai/WanVideo_comfy/blob/cecefb7460b80baa927df0092eee4853e61d4a11/Wan2_1_VAE_bf16.safetensors

```
hfd.sh Kijai/WanVideo_comfy \
--include Wan2_1_VAE_bf16.safetensors \
--local-dir /root/autodl-tmp/models/vae
```

**Distill LoRA**: models/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors

https://huggingface.co/Kijai/WanVideo_comfy/blob/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors

```
hfd.sh Kijai/WanVideo_comfy \
--include lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors \
--local-dir /root/autodl-tmp/models/loras
```

*(对应 JSON 节点 138，强度设为 0.8)*

**五、 JSON 工作流核心逻辑解析**

基于您提供的 JSON，系统运行逻辑如下：

**模型装载 (Node 122):** 启用 sageattn 模式，并挂载 torch_compile。通过 block_swap 设置为 30，允许显存在内存间置换，防止 24G 显存溢出。使用5090 32GB的话，可以把block swap调至0或者5，这样可以加速推理。

**音频解析 (Node 194):** MultiTalkWav2VecEmbeds 节点将输入的 音乐素材2.m4a 转化为 25FPS 的面部驱动序列。

**图像预处理 (Node 171):** 将参考图强制缩放为 480x832 尺寸（Wan2.1 480p 版本的最佳输入分辨率）。

**采样迭代 (Node 128):**

**Steps: 4** — 由于启用了 Distill LoRA，仅需 4 步即可成像。

**Scheduler: flowmatch_distill** — 专为加速 LoRA 设计的调度算法。

**视频合成 (Node 131):** 将解码后的图像序列与原始音频压制为 H264 MP4 视频。

**六、 深度加速分析**

|                      |                                                   |                                                      |
|----------------------|---------------------------------------------------|------------------------------------------------------|
| 技术手段             | 原理说明                                          | 实验增益                                             |
| **SageAttention**    | 针对 Wan2.1 的全注意力机制进行了稀疏化/切片处理。 | **显存节省约 40%**，使 14B 模型能跑出更长秒数。      |
| **FP8 Quantization** | 将权重从 BF16 压缩至 FP8。                        | **显存占用减半**，推理速度提升约 30%。               |
| **Distill LoRA**     | 通过知识蒸馏，减少采样步数。                      | **渲染速度提升 1200%**（从 50 步降至 4 步）。        |
| **Block Swapping**   | 将暂不计算的模型 Block 移至 CPU RAM。             | **打破物理显存壁垒**，24G 显卡可运行 30G+ 的模型流。 |
| **Torch Compile**    | 实时编译 Triton 内核。                            | **端到端推理时间进一步缩短 15%**。                   |

**七、 运行指南**

启动 ComfyUI：

```bash
python main.py --port=8188 --listen=0.0.0.0 --enable-manager

# for autodl
python main.py --port=6006 --listen=0.0.0.0 --enable-manager
```

AutoDl访问ComfyUI参考：

https://www.autodl.com/docs/port/

**注意事项：**

**首次运行：** 由于 torch_compile 会在第一次点击 Queue Prompt 时进行内核编译，后台会卡住约 5-8 分钟，请勿关闭，后续运行将恢复正常速度。

**显存监控：** 运行 watch -n 1 nvidia-smi 监控，如果显存依然告急，请在 Node 134 中将 blocks_to_swap 调高。

infinitetalk单人 (4).json

API 入口对应的json文件

infinitetalk单人 (3).json

|                         |                         |
|-------------------------|-------------------------|
| **\[虚拟人效果1.mp4\]** | **\[虚拟人效果2.mp4\]** |

**八、 自动化调用：文件上传与任务提交**

在远程调用时，你需要先将本地素材推送到服务器。

**1. 文件上传逻辑**

ComfyUI 提供了一个 /upload/image 接口。**注意：** 虽然接口名叫 image，但它同样支持上传音频（.m4a, .wav, .mp3）文件。

**2. Python 自动化调用脚本**

```python
import json
import requests
import os

# 服务器配置
SERVER_ADDR = "http://你的服务器IP:8188"

def upload_file(file_path):
    """将本地文件上传到服务器的 input 目录"""
    with open(file_path, 'rb') as f:
        # ComfyUI 统一使用 /upload/image 接口接收 input 素材
        files = {"image": (os.path.basename(file_path), f)}
        response = requests.post(f"{SERVER_ADDR}/upload/image", files=files)
        if response.status_code == 200:
            print(f"成功上传文件: {os.path.basename(file_path)}")
            return response.json()['name']  # 返回服务器保存的文件名
        else:
            raise Exception(f"上传失败: {response.text}")

def run_infinitetalk_api(local_img, local_audio, prompt_text):
    # 第一步：上传素材到服务器
    server_img_name = upload_file(local_img)
    server_audio_name = upload_file(local_audio)

    # 第二步：加载工作流 JSON (必须是 API 格式)
    with open("infinitetalk_api_workflow.json", 'r') as f:
        workflow = json.load(f)

    # 第三步：修改 JSON 中的参数，指向服务器上刚上传的文件名
    workflow["125"]["inputs"]["audio"] = server_audio_name  # 音频节点
    workflow["133"]["inputs"]["image"] = server_img_name  # 图像节点
    workflow["135"]["inputs"]["positive_prompt"] = prompt_text  # 提示词节点

    # 第四步：发送任务请求
    p = {"prompt": workflow}
    res = requests.post(f"{SERVER_ADDR}/prompt", json=p)
    print(f"任务已提交，Prompt ID: {res.json()['prompt_id']}")

# 执行调用
if __name__ == "__main__":
    run_infinitetalk_api(
        local_img="D:/assets/face.png",
        local_audio="D:/assets/speech.m4a",
        prompt_text="一个穿着职业装的女性在办公室开心地说话，背景模糊",
    )
```

**3. 部署后调用的关键点**

**文件覆盖风险**：上传接口如果遇到同名文件，默认可能会覆盖或自动重命名。建议上传前在本地对文件名加时间戳。

**输入路径一致性**：Node 125 (LoadAudio) 和 Node 133 (LoadImage) 会在服务器的 ComfyUI/input/ 路径下寻找刚才上传的文件。

**结果获取**：任务完成后，你可以通过 /history/{prompt_id} 接口获取输出视频的下载链接，或者直接去服务器 ComfyUI/output/ 目录下查看。
