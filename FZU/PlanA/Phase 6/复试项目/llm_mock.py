import json
import random
import time

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

agent_types = {
    '编写': ['agent_a', 'keyword_a'],
    '执行': ['agent_b', 'keyword_b']
}


# ========== 从JSON文件读取Mock数据（完全解耦） ==========
def load_mock_data():
    try:
        # 打开JSON文件，encoding=utf-8 防止中文乱码
        with open("mock.json", "r", encoding="utf-8") as f:
            return json.load(f)  # 直接转成Python字典
    except FileNotFoundError:
        print("警告：mock_data.json 文件不存在，返回空字典")
        return {}
    except json.JSONDecodeError:
        print("警告：mock_data.json 格式错误，返回空字典")
        return {}


# 加载数据
MOCK_DATA = load_mock_data()


def generate_stream_response(response_text, request_id, model_name):
    """生成OpenAI标准流式响应chunks"""

    # 初始chunk（空内容）
    initial_chunk = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None
            }
        ]
    }
    yield f"data: {json.dumps(initial_chunk)}\n\n"

    # 按行分割响应文本
    lines = response_text.split('\n')

    # 逐行发送内容chunks
    for i, line in enumerate(lines):
        time.sleep(0.05)  # 模拟延迟，可根据需要调整

        # 如果是最后一行，添加换行符
        if i == len(lines) - 1:
            content = line
        else:
            content = line + '\n'

        content_chunk = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": content},
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(content_chunk)}\n\n"

    # 结束chunk（设置finish_reason）
    final_chunk = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"

    # 发送结束标记
    yield "data: [DONE]\n\n"


# ========== 1. GET /v1/models 接口（返回模型列表，符合OpenAI规范） ==========
@app.route("/v1/models", methods=["GET"])
def list_models():
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "your-local-12b-model",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "self",
                "root": "your-local-12b-model",
                "parent": None,
                "permission": [{"id": "perm-123", "object": "model_permission", "created": int(time.time())}]
            }
        ]
    })


# ========== 2. POST /v1/responses 接口（Mock返回，保持格式合规） ==========
@app.route("/v1/responses", methods=["POST"])
def responses():
    _ = request.get_json()
    return jsonify({
        "id": f"resp-{int(time.time())}",
        "object": "response",
        "created": int(time.time()),
        "model": "your-local-12b-model",
        "choices": [{"text": "Mock响应：接口格式符合OpenAI规范", "index": 0}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    })


# ========== 3. POST /v1/chat/completions 接口（核心：代码生成，用Mock数据匹配） ==========
@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    try:
        data = request.get_json()

        # 提取用户消息和系统提示
        user_msg = ""
        prompt = ""
        for msg in data.get("messages", []):
            if msg.get("role") == "user":
                user_msg = msg.get("content", "").lower()
            elif msg.get("role") == "system" and not prompt:
                prompt = msg.get("content", "").lower()

        # 如果没有找到user消息，使用最后一条消息
        if not user_msg and data.get("messages"):
            user_msg = data["messages"][-1].get("content", "").lower()

        # Agent类型匹配（保持原有逻辑）
        agent_type = random.choice(list(agent_types.keys()))
        for a_type in agent_types.keys():
            if a_type in prompt:
                agent_type = a_type
                break

        # Mock数据匹配（保持原有逻辑）
        mock_dict = random.choice(MOCK_DATA['mock'])
        use_random = True
        for m_dict in MOCK_DATA['mock']:
            print(m_dict[agent_types[agent_type][1]])
            if m_dict[agent_types[agent_type][1]].lower() in user_msg:
                mock_dict = m_dict
                use_random = False
                break
        print(use_random)

        # 获取响应内容
        resp_agent = mock_dict[agent_types[agent_type][0]]
        if '```' not in resp_agent:
            resp_agent = resp_agent.replace('\r\n', '\r\n\r\n')

        # 生成请求ID
        request_id = f"chat-{int(time.time())}"
        model_name = "your-local-12b-model"

        # 判断是否为流式请求（默认true）
        stream = data.get("stream", True)

        if stream:
            # 流式返回
            return Response(
                generate_stream_response(resp_agent, request_id, model_name),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 非流式返回（保持原有格式）
            return jsonify({
                "id": request_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": resp_agent
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(user_msg),
                    "completion_tokens": len(resp_agent),
                    "total_tokens": len(user_msg) + len(resp_agent)
                }
            })

    except Exception as e:
        return jsonify({"error": {"message": str(e), "type": "invalid_request_error"}}), 500


# ========== 4. POST /v1/completions 接口（文本补全，Mock返回） ==========
@app.route("/v1/completions", methods=["POST"])
def completions():
    data = request.get_json()
    prompt = data.get("prompt", "")
    return jsonify({
        "id": f"cmpl-{int(time.time())}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": "your-local-12b-model",
        "choices": [
            {
                "text": f"Mock补全结果：{prompt} → 补全内容（接口格式合规）",
                "index": 0,
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": len(prompt), "completion_tokens": 15, "total_tokens": len(prompt) + 15}
    })


# ========== 5. POST /v1/embeddings 接口（嵌入向量，Mock随机生成） ==========
@app.route("/v1/embeddings", methods=["POST"])
def embeddings():
    data = request.get_json()
    input_text = data.get("input", "默认输入")
    # 生成1536维随机嵌入向量（模拟OpenAI的text-embedding-ada-002维度）
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    return jsonify({
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": 0,
                "embedding": embedding
            }
        ],
        "model": "your-local-12b-model",
        "usage": {"prompt_tokens": len(input_text), "total_tokens": len(input_text)}
    })


if __name__ == "__main__":
    # 启动服务：localhost:4321（固定端口）
    app.run(
        host="0.0.0.0",  # 允许外部访问（比如LangFlow调用）
        port=4321,  # 你指定的端口
        debug=False,  # 开发模式，方便调试
        threaded=True  # 支持并发流式请求
    )
