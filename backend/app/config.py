import os
from dotenv import load_dotenv

from pathlib import Path

# Resolve the .env file located one level above the current directory
env_path = Path(__file__).resolve().parent.parent / ".env"

# Load environment variables from .env
load_dotenv(dotenv_path=env_path, override=True)  # Ensure it overrides defaults

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

print(f"✅ Loaded ENV: HOST={HOST}, PORT={PORT}")
