"""Load and save JSON data files for the bidding analysis system."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_json(filepath: str) -> dict:
    """Load a single JSON file, return parsed dict. Returns empty dict if file not found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_competitors(base_dir: str = DATA_DIR) -> dict:
    """Load all competitor JSON files from data/competitors/.
    Returns dict keyed by vendor filename stem, e.g. {'xiwo': {...}, 'honghe': {...}}."""
    comp_dir = os.path.join(base_dir, "competitors")
    competitors = {}
    if not os.path.isdir(comp_dir):
        return competitors
    for fname in os.listdir(comp_dir):
        if fname.endswith(".json"):
            key = fname.replace(".json", "")
            data = load_json(os.path.join(comp_dir, fname))
            if data:
                competitors[key] = data
    return competitors


def load_xunfei(base_dir: str = DATA_DIR) -> dict:
    """Load iFLYTEK parameters from data/xunfei/xunfei.json."""
    return load_json(os.path.join(base_dir, "xunfei", "xunfei.json"))


def load_bid(base_dir: str = DATA_DIR, filename: str = "sample-bid.json") -> dict:
    """Load a bidding file from data/samples/."""
    return load_json(os.path.join(base_dir, "samples", filename))


def save_json(data: dict, filepath: str) -> None:
    """Save dict as JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
