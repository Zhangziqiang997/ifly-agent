"""Load configuration from .env file. NEVER commit .env to git."""
import os

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


def load_env():
    """Load .env file into os.environ. Returns dict of loaded keys."""
    loaded = {}
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
                    loaded[key] = value
    except FileNotFoundError:
        pass  # .env is optional (CI may inject vars directly)
    return loaded


# Auto-load on import
load_env()

# DeepSeek config
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
