import json
import os
import gradio as gr
from pathlib import Path
import modules.scripts as scripts
from modules import script_callbacks, devices

# --- LOG PER DEBUG ---
print("\n[Prompt Architect] Loading extension...")

# --- PERCORSI ---
# scripts.basedir() restituisce il percorso della cartella dell'estensione
BASE_DIR = Path(scripts.basedir())
MODELS_DIR = BASE_DIR / "models"
MODELS_JSON = BASE_DIR / "models.json"

# Crea la cartella models se non esiste per evitare errori
if not MODELS_DIR.exists():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

# --- GESTIONE MODELLI ---
try:
    from llama_cpp import Llama
    HAS_LLAMA = True
    print("[Prompt Architect] Llama-cpp-python detected correctly.")
except ImportError:
    HAS_LLAMA = False
    print("[Prompt Architect] WARNING: Llama-cpp-python not found. GGUF models will not work.")

try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

class PromptGenerator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_type = None
        self.current_path = ""

    def load_model(self, path):
        if self.current_path == path:
            return None
        
        self.model = None
        self.tokenizer = None

        try:
            if path.endswith(".gguf"):
                if not HAS_LLAMA:
                    return "Error: Install llama-cpp-python for GGUF models."
                self.model = Llama(model_path=path, n_ctx=1024, n_gpu_layers=-1)
                self.model_type = "gguf"
            else:
                if not HAS_TRANSFORMERS:
                    return "Error: Transformers library not found."
                self.tokenizer = GPT2Tokenizer.from_pretrained(path)
                self.model = GPT2LMHeadModel.from_pretrained(path).to(devices.device)
                self.model_type = "transformers"
            
            self.current_path = path
            return None
        except Exception as e:
            return f"Error loading: {str(e)}"

    def generate(self, prompt, params):
        try:
            if self.model_type == "gguf":
                # Template ultra-ristretto per evitare chiacchiere
                full_prompt = (
                    f"<|im_start|>system\n"
                    f"You are a professional Stable Diffusion prompt engineer. "
                    f"Your task is to expand the user's idea into a detailed, high-quality prompt. "
                    f"REPLY ONLY WITH THE PROMPT. DO NOT INTRODUCE YOUR RESPONSE. "
                    f"DO NOT SAY 'SURE' OR 'HERE IS'. ONLY OUTPUT THE RAW PROMPT TEXT."
                    f"<|im_end|>\n"
                    f"<|im_start|>user\n"
                    f"Expand this idea into a detailed Stable Diffusion prompt: {prompt}<|im_end|>\n"
                    f"<|im_start|>assistant\n"
                )
                
                output = self.model(
                    full_prompt,
                    max_tokens=params['max_length'],
                    temperature=params['temp'],
                    # Abbiamo rimosso "\n" dagli stop per permettere prompt lunghi
                    stop=["<|im_end|>", "<|im_start|>", "User:"] 
                )
                
                text = output['choices'][0]['text'].strip()
                
                # Pulizia extra nel caso il modello ignori le istruzioni e provi a fare il simpatico
                prefixes_to_remove = [
                    "Sure", "Here is", "Here's", "Detailed prompt:", 
                    "Stable Diffusion Prompt:", "Detailed Stable Diffusion prompt:"
                ]
                for prefix in prefixes_to_remove:
                    if text.startswith(prefix):
                        # Se trova il prefisso, cerca di prendere tutto quello che c'è dopo i due punti
                        if ":" in text:
                            text = text.split(":", 1)[1].strip()
                
                return text
            else:
                # Logica per modelli Transformers (GPT-2 ecc) rimane uguale
                input_ids = self.tokenizer(prompt, return_tensors='pt').input_ids.to(devices.device)
                outputs = self.model.generate(
                    input_ids,
                    do_sample=True,
                    temperature=params['temp'],
                    max_length=params['max_length'],
                    num_return_sequences=1,
                    repetition_penalty=1.2
                )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            return f"Generation error: {str(e)}"

# Inizializza il generatore
gen = PromptGenerator()

def get_models_list():
    choices = {}
    # Da JSON
    if MODELS_JSON.exists():
        try:
            with open(MODELS_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for m in data: choices[f"HF: {m['Title']}"] = m['Model']
        except: pass
    
    # Da cartella models
    if MODELS_DIR.exists():
        for f in os.listdir(MODELS_DIR):
            p = str(MODELS_DIR / f)
            if f.endswith(".gguf"): choices[f"GGUF: {f}"] = p
            elif os.path.isdir(p) and (Path(p)/"config.json").exists():
                choices[f"Local: {f}"] = p
    return choices

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(label="Basic idea", placeholder="Es: Cyberpunk city, neon lights...")
                
                # Carichiamo la lista modelli all'apertura
                m_list = get_models_list()
                model_dropdown = gr.Dropdown(
                    choices=list(m_list.keys()), 
                    label="Select Model",
                    value=list(m_list.keys())[0] if m_list else None
                )
                
                with gr.Row():
                    temp_slider = gr.Slider(0.1, 1.2, 0.7, label="Creativity")
                    max_len_slider = gr.Slider(20, 400, 150, step=1, label="Length")
                
                generate_btn = gr.Button("Generate ✨", variant="primary")

            with gr.Column():
                output_text = gr.Textbox(label="Result", lines=10)
                send_btn = gr.Button("🚀 Send to txt2img")

        # Logica del bottone Genera
        def process(m_name, p, t, ml):
            if not m_name: return "Select a model first!"
            path = get_models_list().get(m_name)
            err = gen.load_model(path)
            if err: return err
            return gen.generate(p, {'temp': t, 'max_length': ml})

        generate_btn.click(process, [model_dropdown, input_text, temp_slider, max_len_slider], output_text)

        # Logica del bottone Invia (JavaScript puro per massima compatibilità)
        send_btn.click(None, output_text, None, _js="""
            (prompt) => {
                // Trova il box del prompt in txt2img (Forge usa questi ID)
                const txt2img_prompt = document.querySelector('#txt2img_prompt textarea');
                if (txt2img_prompt) {
                    txt2img_prompt.value = prompt;
                    // Notifica a Gradio che il valore è cambiato
                    txt2img_prompt.dispatchEvent(new Event('input', { bubbles: true }));
                    // Torna alla tab principale (txt2img)
                    document.querySelector('#tabs').querySelectorAll('button')[0].click();
                } else {
                    alert('Errore: non ho trovato il campo di testo in txt2img.');
                }
            }
        """)

    return (ui, "Prompt Architect", "prompt_arch_tab"),

# Registra la tab
script_callbacks.on_ui_tabs(on_ui_tabs)
print("[Prompt Architect] Tab registered successfully.\n")