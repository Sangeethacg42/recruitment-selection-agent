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
    print("[INFO] Starting Latest 3-Step Recruitment AI Agent on Port 8000...")
    print(f"[INFO] DeepSeek Base URL: {config.DEEPSEEK_BASE_URL}")
    print(f"[INFO] DeepSeek Model: {config.DEEPSEEK_MODEL}")
    
    demo = create_ui()
    
    # Fresh Dedicated Port 8000
    PORT = 8000
    print(f"[INFO] Access the latest 3-Step Recruitment AI Agent at http://127.0.0.1:{PORT}")
    
    try:
        demo.launch(
            server_name="127.0.0.1",
            server_port=PORT,
            css=CSS,
            theme=gr.themes.Soft(),
            share=False
        )
    except OSError:
        demo.launch(
            server_name="127.0.0.1",
            server_port=8080,
            css=CSS,
            theme=gr.themes.Soft(),
            share=False
        )
