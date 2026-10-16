## Accuracy on GSM8K (n=100)

| model | size | accuracy | strict | format | tok_s | truncated |
|---|---|---|---|---|---|---|
| Llama 3.2 1B q3_K_M | 0.7 GB | 32% [24%–42%] | 28% | 87% | 75 | 4% |
| Llama 3.2 1B q4_K_M | 0.8 GB | 44% [35%–54%] | 40% | 90% | 70 | 3% |
| Llama 3.2 1B q6_K | 1.0 GB | 45% [36%–55%] | 37% | 81% | 57 | 1% |
| Llama 3.2 1B q8_0 | 1.3 GB | 45% [36%–55%] | 37% | 83% | 49 | 1% |
| Llama 3.2 1B fp16 | 2.5 GB | 43% [34%–53%] | 35% | 81% | 33 | 1% |
| Gemma 3 1B QAT q4 | 1.0 GB | 43% [34%–53%] | 43% | 91% | 59 | 9% |
| Gemma 3 1B q4_K_M | 0.8 GB | 44% [35%–54%] | 44% | 94% | 52 | 5% |
| Gemma 3 1B fp16 | 2.0 GB | 36% [27%–46%] | 35% | 92% | 37 | 6% |
| Qwen 3.5 2B q4_K_M | 1.9 GB | 73% [64%–81%] | 73% | 92% | 37 | 7% |
| Qwen 3.5 2B q8_0 | 2.7 GB | 72% [63%–80%] | 71% | 89% | 31 | 11% |

## Paired comparisons (exact McNemar)

| question | A | B | acc_A | acc_B | A_only | B_only | p |
|---|---|---|---|---|---|---|---|
| Q1 | Llama q3_K_M | Llama fp16 | 32% | 43% | 11 | 22 | 0.080 |
| Q1 | Llama q4_K_M | Llama fp16 | 44% | 43% | 12 | 11 | 1.000 |
| Q1 | Llama q6_K | Llama fp16 | 45% | 43% | 12 | 10 | 0.832 |
| Q1 | Llama q8_0 | Llama fp16 | 45% | 43% | 7 | 5 | 0.774 |
| Q1 | Llama q3_K_M | Llama q4_K_M | 32% | 44% | 9 | 21 | 0.043 |
| Q2 | Gemma QAT q4 | Gemma q4_K_M | 43% | 44% | 11 | 12 | 1.000 |
| Q2 | Gemma QAT q4 | Gemma fp16 | 43% | 36% | 13 | 6 | 0.167 |
| Q2 | Gemma q4_K_M | Gemma fp16 | 44% | 36% | 16 | 8 | 0.152 |
| Q3 | Qwen q4_K_M | Llama fp16 | 73% | 43% | 37 | 7 | 0.000 |
| Q3 | Qwen q4_K_M | Gemma fp16 | 73% | 36% | 38 | 1 | 0.000 |
| Q3 | Qwen q4_K_M | Qwen q8_0 | 73% | 72% | 7 | 6 | 1.000 |

## Contamination probe (20 originals × 5 variants)

| model | original | variants | gap |
|---|---|---|---|
| Llama 3.2 1B q3_K_M | 25% | 21% | +4% [-10%, +19%] |
| Llama 3.2 1B q4_K_M | 40% | 41% | -1% [-20%, +19%] |
| Llama 3.2 1B q6_K | 30% | 40% | -10% [-26%, +8%] |
| Llama 3.2 1B q8_0 | 25% | 43% | -18% [-36%, -2%] |
| Llama 3.2 1B fp16 | 40% | 42% | -2% [-27%, +22%] |
| Gemma 3 1B QAT q4 | 30% | 39% | -9% [-19%, -0%] |
| Gemma 3 1B q4_K_M | 40% | 29% | +11% [-0%, +24%] |
| Gemma 3 1B fp16 | 15% | 24% | -9% [-19%, -2%] |
| Qwen 3.5 2B q4_K_M | 55% | 61% | -6% [-17%, +4%] |
| Qwen 3.5 2B q8_0 | 65% | 66% | -1% [-16%, +11%] |

Pooled gap: -4.1% [-9.3%, +0.9%]
