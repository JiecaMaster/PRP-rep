微调数据集构造格式：
[
  {
    "instruction": "人类指令（必填）",
    "input": "人类输入（选填）",
    "output": "模型回答（必填）",
    "system": "系统提示词（选填）",
    "history": [
      ["第一轮指令（选填）", "第一轮回答（选填）"],
      ["第二轮指令（选填）", "第二轮回答（选填）"]
    ]
  }
]
最终输入会由instruction 和 input组合而成。

llama factory启动示例：
CUDA_VISIBLE_DEVICES=0,1 python src/webui.py \
    --model_name_or_path /root/autodl-tmp/models/modelscope/hub/Qwen/Qwen2.5-14B-Instruct \
    --template qwen \
    --infer_backend vllm \
        --vllm_enforce_eager

启动后选取共享链接：需要挂梯子使用

共享链接启用：将src/webui中的share指定为True，按照报错安装相应程序，为该程序指定chmod +x 后重试。

解决显存不足的方法：目前尝试了DDP和DeepSpeed Stage 2/3，有问题或与模型本身分词器策略冲突，未能根据报错找到问题；减少batch size为每张GPU1个，使用DeepSpeed offload。