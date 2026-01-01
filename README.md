# sd-forge-prompt-architect
Prompt generator with personal template locally
# Forge Prompt Architect 🚀

**Forge Prompt Architect** is a next-generation prompt expansion extension specifically designed for **Stable Diffusion Forge** and **WebUI**. 

While most prompt generators are stuck with old GPT-2 technology, this extension brings the power of modern Large Language Models (LLMs) like **Qwen 2.5**, **Llama 3**, and **Mistral** directly into your creative workflow. By supporting the **GGUF** format, it allows you to generate highly intelligent, descriptive, and context-aware prompts with minimal VRAM usage.

![Preview](preview.png)

## ✨ Key Features

- 🧠 **Modern LLM Support:** Full integration with **GGUF** models via `llama-cpp-python` for superior prompt intelligence.
- ⚡ **Seamless Integration:** Send your generated prompts to the `txt2img` tab with a single click. No more copy-pasting.
- 🎨 **Dynamic Expansion:** Transform a simple idea (e.g., "a cat") into a professional-grade prompt with lighting, atmosphere, and technical details.
- 📂 **Versatile Model Management:** 
  - Support for local **GGUF** files.
  - Support for standard **Transformers** models (GPT-2, GPT-Neo, etc.).
  - Remote model loading from Hugging Face.
- 🛠️ **Fine-Tuned Control:** Adjust creativity (Temperature) and output length to match your specific needs.

---

## 📦 Installation

### 1. Install the Extension
1. Open your Stable Diffusion Forge / WebUI.
2. Navigate to the **Extensions** tab > **Install from URL**.
3. Paste the URL of this GitHub repository and click **Install**.

### 2. Install Dependencies (Mandatory for GGUF)
To use modern GGUF models, you must install the `llama-cpp-python` library inside your Forge environment.
1. Open a terminal/command prompt in your main `stable-diffusion-webui-forge` folder.
2. Run the following command:

**Windows:**
```
.\venv\Scripts\python.exe -m pip install llama-cpp-python
```
**Linux:**
```
./venv/bin/python -m pip install llama-cpp-python
```
## 📂 Adding Your Models ##
### Using GGUF Models (Highly Recommended)
1. Download a .gguf file from Hugging Face (we recommend Qwen2.5-7B-Instruct-GGUF).
2. Place the downloaded file into: extensions/sd-forge-prompt-architect/models/.
3. The model will appear in the dropdown menu with the prefix GGUF:.
### Using Transformers Models
- Standard Models: Add the Hugging Face Model ID to the ```models.json``` file located in the extension root.
- Local Folders: Place the model folder (containing ```config.json``` and weights) inside the ```models/ directory```.
## 🛠 Usage
1. Select a Model: Choose your preferred AI from the dropdown.
2. Enter Your Idea: Type a simple concept in the "Idea Base" box.
3. Configure: Adjust the Creativity slider (higher = more random) and Length.
4. Generate ✨: Click the button and wait a few seconds for the AI to craft your prompt.
5. Send to txt2img 🚀: Click the button to automatically populate the main Forge prompt box and switch to the generation tab.

## 🤝 Contributing
Contributions are welcome! If you have ideas for new features or find any bugs, please open an Issue or submit a Pull Request.
