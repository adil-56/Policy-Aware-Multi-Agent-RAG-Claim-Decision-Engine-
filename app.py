import uvicorn
from backend.main import app
import spaces

# Dummy function to appease Hugging Face ZeroGPU monitor
@spaces.GPU
def _dummy_gpu():
    pass

# Hugging Face Spaces (Gradio SDK) expects an app.py in the root directory
# and routes traffic to port 7860.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
