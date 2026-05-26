
"""
Convert nanoGPT checkpoint to HuggingFace format
So we can use llama.cpp's official convert-hf-to-gguf.py
"""

import argparse
import torch
from pathlib import Path
import json
from transformers import GPT2Tokenizer


def main():
    parser = argparse.ArgumentParser(description="Convert nanoGPT checkpoint to HuggingFace format")
    parser.add_argument("--input", "-i", type=Path, help="Input nanoGPT checkpoint", required=True)
    parser.add_argument("--output", "-o", type=Path, help="Output HF directory", required=True)
    args = parser.parse_args()

    print(f"Loading checkpoint from {args.input}...")
    checkpoint = torch.load(args.input, map_location="cpu")

    model_state = checkpoint["model"]
    model_args = checkpoint["model_args"]

    print("Model args:", model_args)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # 1. Save config.json
    config = {
        "architectures": ["GPT2LMHeadModel"],  # Add this!
        "vocab_size": model_args.get("vocab_size"),
        "n_positions": model_args.get("block_size"),
        "n_ctx": model_args.get("block_size"),
        "n_embd": model_args.get("n_embd"),
        "n_layer": model_args.get("n_layer"),
        "n_head": model_args.get("n_head"),
        "n_inner": 4 * model_args.get("n_embd"),
        "activation_function": "gelu_new",
        "layer_norm_epsilon": 1e-5,
        "initializer_range": 0.02,
        "use_cache": True,
        "model_type": "gpt2",
        "task_specific_params": {"text-generation": {"do_sample": True, "max_length": 50}}
    }

    config_path = args.output / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print(f"Created config at {config_path}")

    # 2. Save tokenizer
    print("Saving GPT2 tokenizer...")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    
    # First save the basic files
    tokenizer.save_pretrained(args.output)
    
    # Manually save vocab.json and merges.txt
    print("Manually saving vocab.json and merges.txt...")
    
    # Save vocab.json
    vocab = tokenizer.get_vocab()
    vocab_file = args.output / "vocab.json"
    with open(vocab_file, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)
    
    # Save merges.txt - let's download the standard GPT-2 merges file
    import urllib.request
    merges_url = "https://huggingface.co/gpt2/resolve/main/merges.txt"
    merges_file = args.output / "merges.txt"
    try:
        urllib.request.urlretrieve(merges_url, merges_file)
        print("  ✓ Downloaded merges.txt from HuggingFace")
    except Exception as e:
        print(f"  ✗ Failed to download merges.txt: {e}")
        # Fallback: create a simple merges.txt (not ideal but better than nothing)
        with open(merges_file, "w", encoding="utf-8") as f:
            f.write("#version: 0.2\n")

    # Verify required files exist
    required_files = ["vocab.json", "merges.txt", "tokenizer.json", "tokenizer_config.json"]
    for filename in required_files:
        file_path = args.output / filename
        if file_path.exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} missing!")

    print(f"Saved tokenizer files to {args.output}")

    # 3. Rename and transpose weights to HuggingFace format
    print("Converting weights...")
    hf_state = {}

    # Weights that need to be transposed (see model.py line 245)
    transposed_suffixes = [
        'attn.c_attn.weight', 
        'attn.c_proj.weight', 
        'mlp.c_fc.weight', 
        'mlp.c_proj.weight'
    ]

    for old_name, tensor in model_state.items():
        new_name = old_name

        # Remove "transformer." prefix
        if new_name.startswith("transformer."):
            new_name = new_name[len("transformer."):]

        # Handle wte/wpe
        if new_name == "wte.weight":
            hf_state["transformer.wte.weight"] = tensor
        elif new_name == "wpe.weight":
            hf_state["transformer.wpe.weight"] = tensor
        elif new_name == "ln_f.weight":
            hf_state["transformer.ln_f.weight"] = tensor
        elif new_name == "ln_f.bias":
            hf_state["transformer.ln_f.bias"] = tensor
        elif new_name.startswith("h."):
            # Transformer layer
            # First rename from nanoGPT to HF:
            # h.0.attn.c_attn.weight -> transformer.h.0.attn.c_attn.weight
            new_name = "transformer." + new_name
            
            # Check if this weight needs to be transposed
            needs_transpose = any(new_name.endswith(suffix) for suffix in transposed_suffixes)
            
            if needs_transpose:
                # Transpose the weight tensor (reverse of what from_pretrained does)
                hf_state[new_name] = tensor.t()
            else:
                hf_state[new_name] = tensor
        # Don't add lm_head! GPT2 uses weight tying, convert-hf-to-gguf.py will handle it!

    # Save the state dict
    pt_path = args.output / "pytorch_model.bin"
    torch.save(hf_state, pt_path)
    print(f"Saved weights to {pt_path}")

    print(f"\nDone! Saved to {args.output}")
    print(f"\nNow you can run: python ../nous-llama.cpp-master/convert-hf-to-gguf.py {args.output} out.gguf 1")


if __name__ == "__main__":
    main()

