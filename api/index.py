import sys
import os

# Add website directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "website"))

from app import app
