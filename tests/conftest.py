import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('MACAST_CONFIG_DIR', tempfile.mkdtemp(prefix='macast-tests-'))
