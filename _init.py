import os
import sys
import logging
from pathlib import Path
import json
import traceback
import datetime
from _subprwrapper import run


def exit(exit_code):
    json.dump(state, open(STATE_PATH, 'w'))
    sys.exit(exit_code)


CONFIG_DIR = os.path.join(str(Path.home()), '.tpcc')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
STATE_PATH = os.path.join(CONFIG_DIR, 'state.json')

DEVNULL = open(os.devnull, 'wb')
DEFAULT_OUTPUT = None
DEFAULT_ERROR  = DEVNULL

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
    repos_path = os.path.expandvars(os.path.expanduser(config['path_to_repos']))
    SOLUTIONS_REPO = os.path.join(repos_path, 'solutions')
    TPCC_REPO = os.path.join(repos_path, config['course_repo_name'])
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
        'task': '',
        'merged_tasks': []
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


def get_string_state_field(field):
    if field not in state:
        state[field] = ''
    return state[field]


def get_list_state_field(field):
    if field not in state:
        state[field] = []
    return state[field]


def current_task():
    return get_string_state_field('task')


def get_merged_tasks():
    return get_list_state_field('merged_tasks')


def checkout_to_current_task():
    checkout = run(['git', 'checkout', current_task()],
                   cwd=SOLUTIONS_REPO,
                   stdout=DEFAULT_OUTPUT,
                   stderr=DEFAULT_ERROR)

    if checkout.returncode != 0:
        logger.error('{} is a configured task but checkout failed'.format(current_task()))
        state['task'] = ''
        exit(1)


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
stream_handler.setFormatter(TaskFormatter())
