# nanoGPT → GGUF 转换流程 - 关键代码

本文件夹包含将 nanoGPT 模型转换为 HuggingFace 格式并最终转换为 GGUF 的关键脚本。

## 📁 文件结构

```
关键代码与数据/
├── README.md                          # 本文件
├── model.py                           # GPT 模型架构定义
├── train.py                           # 训练脚本（配置已内化）
├── nanogpt_to_hf.py                   # 转换脚本：checkpoint → HuggingFace
├── data/
│   └── shakespeare/
│       ├── prepare.py                 # 数据准备脚本
│       ├── input.txt                  # Shakespeare 原始文本
│       ├── train.bin                  # 训练数据（GPT-2 BPE 编码）
│       ├── val.bin                    # 验证数据
│       └── readme.md
└── [output/]                         # 训练输出目录（运行时生成）
    └── ckpt.pt                       # 模型检查点
```

## 🔄 完整工作流程

### Step 1: 准备数据（已完成）
```bash
cd data/shakespeare
python prepare.py
```
这会下载 Shakespeare 数据集并使用 GPT-2 BPE tokenizer 编码。

### Step 2: 训练模型
```bash
cd ..
python train.py
```
训练 100 步（可在 train.py 开头修改 max_iters）

### Step 3: 转换为 HuggingFace 格式
```bash
python nanogpt_to_hf.py --input out-mini-gpt2/ckpt.pt --output hf_model
```
生成 HuggingFace 格式的模型文件：
- config.json
- vocab.json
- merges.txt
- tokenizer.json
- tokenizer_config.json
- pytorch_model.bin

### Step 4: 转换为 GGUF 格式
```bash
python ../nous-llama.cpp-master/convert-hf-to-gguf.py --outfile out.gguf --outtype f16 hf_model
```
或
```bash
python ../nous-llama.cpp-master/convert-hf-to-gguf.py --outfile out.gguf --outtype f16 hf_model
```

### Step 5: 在 LM Studio 中加载
将 `out.gguf` 拖入 LM Studio 即可。

## ⚠️ 重要说明

### 关于 EOS Token
本模型在训练时**未使用 EOS token**，因此模型无法主动停止生成。解决方案：
1. 在 LM Studio 中设置合理的 max_tokens 上限（如 200-500）
2. 或配置自定义的 stop 序列（如 `\n\n`）

### 关于权重转置
model.py 第 245 行定义了需要转置的权重层（用于兼容 HuggingFace 格式）：
- attn.c_attn.weight
- attn.c_proj.weight
- mlp.c_fc.weight
- mlp.c_proj.weight

## 📊 模型配置

| 参数 | 值 |
|------|-----|
| n_layer | 4 |
| n_head | 4 |
| n_embd | 256 |
| block_size | 256 |
| vocab_size | 50,304 |
| bias | True |
| max_iters | 100 |

## 🔧 依赖

- Python 3.8+
- PyTorch 2.0+
- numpy
- tiktoken
- transformers
- python-docx（仅用于生成文档）
