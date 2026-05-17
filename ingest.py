import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tools.bootstrap

import json
from tools.vector_search import ingest

with open('data/knowledge_base.json', 'r') as f:
    docs = json.load(f)

ingest(docs)

print(f"Knowledge base ready — {len(docs)} docs ingested.")
