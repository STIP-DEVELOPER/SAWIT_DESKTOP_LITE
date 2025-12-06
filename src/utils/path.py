from os.path import dirname, abspath, join

ROOT = dirname(dirname(__file__))

ROOT_DIR = dirname(dirname(dirname(abspath(__file__))))
LOGS_DIR = join(ROOT_DIR, "logs")
DATA_JSON = join(LOGS_DIR, "data.json")

MODELS_DIR = join(ROOT_DIR, "models")
