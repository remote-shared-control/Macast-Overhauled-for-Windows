import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, os.environ.get('MACAST_SOURCE', str(Path(__file__).resolve().parents[2])))
os.environ.setdefault('MACAST_CONFIG_DIR', tempfile.mkdtemp(prefix='macast-nva-tests-'))
