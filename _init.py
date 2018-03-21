import os
import sys
import logging
from pathlib import Path
import json
import traceback
import datetime
from _subprwrapper import run

CONFIG_DIR = os.path.join(str(Path.home()), '.tpcc')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
STATE_PATH = os.path.join(CONFIG_DIR, 'state.json')

DEVNULL = open(os.devnull, 'wb')
DEFAULT_OUTPUT = None
DEFAULT_ERROR  = None

logger = logging.getLogger('tpcc')

log_file_handler = logging.FileHandler(os.path.join(CONFIG_DIR, 'tpcc.log'))
log_file_handler.setLevel(logging.INFO)

debug_log_file_handler = logging.FileHandler(os.path.join(CONFIG_DIR, 'tpcc-debug.log'))
debug_log_file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)

logger.addHandler(log_file_handler)
logger.addHandler(debug_log_file_handler)
logger.addHandler(stream_handler)

try:
    with open(CONFIG_PATH) as json_config:
        config = json.load(json_config)
except FileNotFoundError:
    logger.error('Configuration file does not exist. Create configuration file before starting the aplication')
    sys.exit(1)
except ValueError:
    logger.error('Malformed configuration file: JSON format expected')
    sys.exit(1)
except Exception as e:
    print(e, file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

try:
    SOLUTIONS_REPO = os.path.join(config['path_to_repos'], 'solutions')
    TPCC_REPO = os.path.join(config['path_to_repos'], config['course_repo_name'])
except KeyError as e:
    logger.error('Key "{}" is missing in configuration file'.format(e.args[0]))
    sys.exit(1)
except Exception as e:
    print(e, file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

try:
    with open(STATE_PATH) as json_state:
        state = json.load(json_state)
except FileNotFoundError:
    state = {
        'task': ''
    }
    with open(STATE_PATH, 'w') as json_state:
        json.dump(state, json_state)
except ValueError:
    logger.error('Malformed state file: JSON format expected')
    sys.exit(1)
except Exception as e:
    print(e, file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)


def current_task():
    return state['task']


if current_task() != '':
    run(['git', 'checkout', current_task()],
        cwd=SOLUTIONS_REPO,
        stdout=DEFAULT_OUTPUT,
        stderr=DEFAULT_ERROR)


class TaskFormatter(logging.Formatter):
    def __init__(self):
        super(TaskFormatter, self).__init__()

    def format(self, record):
        return '[{}] [task {}] {}: {}'.format(
            datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            current_task(),
            record.levelname,
            record.msg
        )


log_file_handler.setFormatter(TaskFormatter())
debug_log_file_handler.setFormatter(TaskFormatter())
