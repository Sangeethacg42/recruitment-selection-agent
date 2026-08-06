import os
import sys
import logging
import gradio as gr

# Ensure src directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from recruitment_agent.config import config
from recruitment_agent.ui import create_ui, CSS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    print("[INFO] Starting Recruitment & Selection AI Agent Gradio App...")
    print(f"[INFO] DeepSeek Base URL: {config.DEEPSEEK_BASE_URL}")
    print(f"[INFO] DeepSeek Model: {config.DEEPSEEK_MODEL}")
    
    demo = create_ui()
    
    ports_to_try = [7895, 7890, 7860, 7861]
    launched = False
    
    for port in ports_to_try:
        try:
            print(f"[INFO] Launching on http://127.0.0.1:{port} ...")
            demo.launch(
                server_name="127.0.0.1",
                server_port=port,
                css=CSS,
                theme=gr.themes.Soft(),
                share=False
            )
            launched = True
            break
        except OSError:
            print(f"[WARNING] Port {port} in use, trying next...")
            continue
            
    if not launched:
        demo.launch(
            server_name="127.0.0.1",
            css=CSS,
            theme=gr.themes.Soft(),
            share=False
        )
