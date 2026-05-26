"""
Sample from a trained model (mini GPT2)
"""
import os
import argparse
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT

# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Sample from trained model')
parser.add_argument('--ckpt', type=str, default='out-mini-gpt2/ckpt.pt', help='Path to checkpoint file')
parser.add_argument('--start', type=str, default='\n', help='Start prompt')
parser.add_argument('--num_samples', type=int, default=3, help='Number of samples to generate')
parser.add_argument('--max_new_tokens', type=int, default=200, help='Max tokens to generate')
parser.add_argument('--temperature', type=float, default=0.8, help='Temperature for sampling')
parser.add_argument('--top_k', type=int, default=200, help='Top-k sampling')
parser.add_argument('--seed', type=int, default=1337, help='Random seed')
parser.add_argument('--device', type=str, default='cuda', help='Device to use')
args = parser.parse_args()

# -----------------------------------------------------------------------------
torch.manual_seed(args.seed)
torch.cuda.manual_seed(args.seed)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
device_type = 'cuda' if 'cuda' in args.device else 'cpu'
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}['float16']
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# Load model from checkpoint
print(f"Loading checkpoint from {args.ckpt}...")
checkpoint = torch.load(args.ckpt, map_location=args.device)
gptconf = GPTConfig(**checkpoint['model_args'])
model = GPT(gptconf)
state_dict = checkpoint['model']
unwanted_prefix = '_orig_mod.'
for k,v in list(state_dict.items()):
    if k.startswith(unwanted_prefix):
        state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
model.load_state_dict(state_dict)

model.eval()
model.to(args.device)

# Use GPT-2 tokenizer
enc = tiktoken.get_encoding("gpt2")
encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

# Encode the beginning of the prompt
start_ids = encode(args.start)
x = (torch.tensor(start_ids, dtype=torch.long, device=args.device)[None, ...])

# Run generation
print(f"\nGenerating {args.num_samples} samples with prompt: {repr(args.start)}")
print("=" * 50)

with torch.no_grad():
    with ctx:
        for k in range(args.num_samples):
            y = model.generate(x, args.max_new_tokens, temperature=args.temperature, top_k=args.top_k)
            print(f"Sample {k+1}:")
            print(decode(y[0].tolist()))
            print('-' * 50)
