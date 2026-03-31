import sys
from pathlib import Path
import json

# Add project root to path for imports
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

try:
    from server import _build_website
    from engine import get_all_posts, load_theory
    
    print("◈ DKB System Synchronization Initiated...")
    
    # Load data
    posts = get_all_posts(200)
    theory = load_theory()
    
    # Regenerate website and graph_data.json
    _build_website(posts, theory)
    
    print("✅ System successfully synchronized.")
    print(f"   - graph_data.json updated in website/")
    print(f"   - index.html updated in website/")
    
except ImportError as e:
    print(f"❌ Error importing DKB modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Synchronization failed: {e}")
    sys.exit(1)
