import uvicorn
from backend.main import app

# Hugging Face Spaces (Gradio SDK) expects an app.py in the root directory
# and routes traffic to port 7860.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
