# testing local chatbot.8GB vram model
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ===== CONFIG =====
model_name = "google/gemma-4-E2B-it" # 8gb vram required , change if you have lower
device = "cuda" if torch.cuda.is_available() else "cpu"

# ===== LOAD MODEL =====
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

# ===== CHAT LOOP =====
chat_history = []

print("🤖 Chatbot ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Store message
    chat_history.append({"role": "user", "content": user_input})

    # Build prompt using chat template
    prompt = tokenizer.apply_chat_template(
        chat_history,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only new response (avoid repeating history)
    response = response[len(prompt):].strip()

    print("Bot:", response)

    # Save bot reply
    chat_history.append({"role": "assistant", "content": response})