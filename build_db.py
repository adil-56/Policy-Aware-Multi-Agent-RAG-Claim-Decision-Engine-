import sys
import os
from dotenv import load_dotenv

# API key check removed, using HuggingFace open-source embeddings

print("Building DB...")
from backend.api.dependencies import get_retriever
get_retriever()
print("DB built successfully!")
