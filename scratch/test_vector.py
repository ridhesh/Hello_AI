import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.bootstrap

import time
print("Starting vector_search import test...")
start = time.time()
from tools.vector_search import search_kb
print(f"Import finished in {time.time() - start:.2f} seconds.")

print("Testing query...")
start = time.time()
res = search_kb("how to get a refund")
print(f"Query returned in {time.time() - start:.2f} seconds. Results:")
print(res)
