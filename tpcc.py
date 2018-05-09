#!/usr/bin/env python3

import argparse
from shutil import which
import git
import shutil
import re
import gitlab

from _init import *
from yes_no import query_yes_no

def add_parser(subparsers, name, description, handlers, action) -> argparse.ArgumentParser:
    handlers[name] = action
    parser = subparsers.add_parser(name, description=description, help=description)
    return parser


def is_theoretical_task(task_name):
    return not os.path.exists(os.path.join(TPCC_REPO, 'tasks', task_name, 'CMakeLists.txt'))


class SetTaskAction:
    def __init__(self):
        self.git = git.Repo(SOLUTIONS_REPO).git

    def run(self, args):
        args.task_name = args.task_name.strip('/')
        if self.branch_exists(args.task_name):
            self.checkout_branch_create(args.task_name)
            state['task'] = args.task_name
            print('Switched to task {}'.format(args.task_name))
            exit(0)
        if args.check_task and not self.is_task_name(args.task_name):
            logger.warning('{} is not a valid task name'.format(args.task_name))
            exit(1)
        self.checkout_branch_create(args.task_name)
        self.create_solution_file(args)
        state['task'] = args.task_name
        print('Switched to task {}'.format(args.task_name))

    # noinspection PyMethodMayBeStatic
    def is_task_name(self, task_name: str):
        if task_name.count('/') != 1:
            return False
        return os.path.isdir(os.path.join(TPCC_REPO, 'tasks', task_name))

    def branch_exists(self, branch_name):
        try:
            self.git.rev_parse('--verify', branch_name)
            return True
        except git.exc.GitCommandError:
            return False

    def checkout_branch_create(self, task_name):
        if self.branch_exists(task_name):
            checkout = run(['git', 'checkout', task_name],
                           cwd=SOLUTIONS_REPO,
                           stdout=DEFAULT_OUTPUT,
                           stderr=DEFAULT_ERROR)
            if checkout.returncode != 0:
                logger.error('Checkout failed with exit code {}'.format(checkout.returncode))
                exit(checkout.returncode)
        else:
            run(['git', 'checkout', 'master'],
                cwd=SOLUTIONS_REPO,
                stdout=DEFAULT_OUTPUT,
                stderr=DEFAULT_ERROR)
            checkout = run(['git', 'checkout', '-b', task_name],
                           cwd=SOLUTIONS_REPO,
                           stdout=DEFAULT_OUTPUT,
                           stderr=DEFAULT_ERROR)
            if checkout.returncode != 0:
                logger.error('Checkout failed with exit code {}'.format(checkout.returncode))
                exit(checkout.returncode)

    # noinspection PyMethodMayBeStatic
    def create_solution_file(self, args):
        solution_dir = os.path.join(SOLUTIONS_REPO, args.task_name)
        if not os.path.exists(os.path.join(TPCC_REPO, 'tasks', args.task_name, 'CMakeLists.txt')):
            self.add_theoretical_solution(args, solution_dir)
        else:
            self.add_practical_solution(args, solution_dir)

    def add_practical_solution(self, args, solution_dir):
        solution_path = os.path.join(solution_dir, 'solution.hpp')
        if os.path.exists(solution_path):
            return

        if args.sol_ref:
            sol_ref = os.path.join(TPCC_REPO, 'tasks', args.task_name, args.sol_ref)
        else:
            ref_file_name = os.path.split(args.task_name)[1].replace('-', '_')
            sol_ref = os.path.join(TPCC_REPO, 'tasks', args.task_name, '{}.hpp'.format(ref_file_name))

        if not args.template:
            os.makedirs(solution_dir, exist_ok=True)
            open(solution_path, 'a').close()
        elif os.path.exists(sol_ref):
            os.makedirs(solution_dir, exist_ok=True)
            shutil.copyfile(sol_ref, solution_path)
        else:
            print("""
Solution template {1} not found. Specify solution template file:
\ttpcc task --template <template_file> {0}
or specify --no-template option to create empty file:
\ttpcc task --no-template {0}
            """.format(args.task_name, os.path.split(sol_ref)[1]))
            logger.error("template not found")
            exit(1)

        self.add_solution_to_git(args.task_name, solution_path)

    def add_theoretical_solution(self, args, solution_dir):
        solution_path = os.path.join(solution_dir, 'solution.md')
        if os.path.exists(solution_path):
            return
        logger.info('{}/CMakeLists.txt not found. Assuming theoretical task'.format(args.task_name))
        os.makedirs(solution_dir, exist_ok=True)
        open(solution_path, 'a').close()
        self.add_solution_to_git(args.task_name, solution_path)

    def add_solution_to_git(self, task_name, solution_path):
        self.checkout_branch_create(task_name)
        run(['git', 'add', solution_path],
            cwd=SOLUTIONS_REPO,
            stdout=DEFAULT_OUTPUT,
            stderr=DEFAULT_ERROR)
        run(['git', 'commit', solution_path, '-m', 'Initial commit for {}'.format(task_name)],
            cwd=SOLUTIONS_REPO,
            stdout=DEFAULT_OUTPUT,
            stderr=DEFAULT_ERROR)
        run(['git', 'push', '--set-upstream', 'origin', task_name],
            cwd=SOLUTIONS_REPO,
            stdout=DEFAULT_OUTPUT,
            stderr=DEFAULT_ERROR)

    @classmethod
    def add_parser(cls, subparsers, handlers):
        subparser = add_parser(
            subparsers, 'task', 'Change current task', handlers, lambda x: cls().run(x)
        )
        subparser.add_argument('-f', '--force',
                               dest='check_task',
                               action='store_false')
        subparser.add_argument('task_name', help='Full task name')
        template = subparser.add_mutually_exclusive_group()
        template.add_argument('-t', '--template',
                              dest='sol_ref',
                              help='Solution template')
        template.add_argument('--no-template',
                              dest='template',
                              action='store_false',
                              help='Create empty file without template')


def status_action(args=None):
    print(current_task())


def config_action(args=None):
    for key, value in config.items():
        print("'{}': '{}'".format(key, value))


def get_clang_compiler():
    clang_compiler = which('clang++-5.0')
    if clang_compiler is None:
        clang_compiler = which('clang++-6.0')
    if clang_compiler is None:
        clang_compiler = which('clang++')
    if clang_compiler is None:
        logger.error('Suitable clang compiler not found')
        exit(1)
    return clang_compiler


def get_build_path():
    if current_task() == '':
        print('No selected task. You should select task first:\n\ttpcc task <task_name>')
        logger.error('task not selected')
        exit(1)

    return os.path.join(TPCC_REPO, 'tasks', current_task(), 'build')


def run_cmake_target(targets):
    build_path = get_build_path()

    if not os.path.exists(os.path.join(build_path, 'Makefile')):
        logger.warning('No Makefile found. Running build')
        build_action()

    return run(['make'] + targets, cwd=build_path)


def build_action(args=None):
    run(['cmake', '..', '-DCMAKE_CXX_COMPILER={}'.format(get_clang_compiler())],
        cwd=get_build_path())


class TestAction:

    @classmethod
    def run(cls, args):
        cls.run_tests(args.flavor)

    @classmethod
    def run_tests(self, flavor):
        dispatcher = {
            'asan':   'run_asan_test',
            'tsan':   'run_tsan_test',
            'unit':   'run_all_unit_tests',
            'stress': 'run_all_stress_tests',
            'all':   'run'
        }

        target = [dispatcher[flavor]]

        testing = run_cmake_target(target)

        if testing.returncode != 0:
            print('Testing failed with exit code {}'.format(testing.returncode))
            exit(testing.returncode)

    @classmethod
    def add_parser(cls, subparsers, handlers):
        subparser = add_parser(
            subparsers, 'test', 'Test the solution', handlers, lambda x: cls().run(x)
        )
        subparser.add_argument('flavor', help='Which tests to run',
                               choices=[
                                   'asan',
                                   'tsan',
                                   'unit',
                                   'stress',
                                   'all'
                               ],
                               nargs='?',
                               default='all',
                               const='all')




# def asan_action(args=None):
#     run_tests('asan')
#
#
# def tsan_action(args=None):
#     run_tests('tsan')
#
#
# def unit_action(args=None):
#     run_tests('unit')
#
#
# def stress_action(args=None):
#     run_tests('stress')
#
#
# def test_action(args=None):
#     run_tests('all')
#

def style_action(args=None):
    run_cmake_target(['style'])


def clean_action(args=None):
    folder = get_build_path()
    for the_file in os.listdir(folder):
        if the_file == '.gitignore':
            continue
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


class CommitTaskAction:
    @classmethod
    def add_parser(cls, subparsers, handlers):
        subparser = add_parser(
            subparsers, 'commit', 'Commit solution changes', handlers, lambda x: cls().run(x)
        )
        subparser.add_argument('-m', '--message',
                               help='Commit message',
                               dest='message',
                               default='{} task solution changed'.format(current_task()))

    def run(self, args):
        self.commit_task(args.message)

    def solution_changed(self, task_name: str):
        repo = git.Repo(SOLUTIONS_REPO)
        run(['git', 'add', task_name],
            cwd=SOLUTIONS_REPO,
            stdout=DEFAULT_OUTPUT,
            stderr=DEFAULT_ERROR)
        diffs = repo.index.diff("HEAD")
        for diff in diffs:
            if re.match('{}/solution.(hpp|md)'.format(task_name), diff.b_path):
                return True
        return False

    def solution_different_from_remote(self, task_name):
        repo = git.Repo(SOLUTIONS_REPO)


    def commit_task(self, message):
        task_name = current_task()
        if self.solution_changed(task_name):
            commit = run(['git', 'commit', task_name, '-m', message],
                         cwd=SOLUTIONS_REPO,
                         stdout=DEFAULT_OUTPUT,
                         stderr=DEFAULT_ERROR)
            if commit.returncode != 0:
                logger.error('Commit failed with exit code {}'.format(commit.returncode))
                exit(commit.returncode)
        else:
            logger.warning('Solution is up-to-date with local repository')

        push = run(['git', 'push', '--set-upstream', 'origin', current_task()],
                   cwd=SOLUTIONS_REPO,
                   stdout=DEFAULT_OUTPUT,
                   stderr=DEFAULT_ERROR)

        if push.returncode != 0:
            logger.error('Push failed with exit code {}'.format(push.returncode))
            exit(push.returncode)


class GitlabMergeAction:
    @classmethod
    def add_parser(cls, subparsers, handlers):
        subparser = add_parser(
            subparsers, 'merge', 'Create merge request', handlers, lambda x: cls().run(x)
        )
        subparser.add_argument('--no-tests',
                               help='do not run tests before creating merge request',
                               dest='test',
                               action='store_false')

    def run(self, args):
        try:
            try:
                group_number = str(config['group_number'])
                first_name = config['first_name']
                last_name = config['last_name']
                gitlab_token = config['gitlab_token']
                assignee_username = config['assignee_username']
                gitlab_repo_user = config['gitlab_repo_user']
            except KeyError as e:
                logger.error('Key "{}" is missing in configuration file'.format(e.args[0]))
                exit(1)

            merged_tasks = get_merged_tasks()

            if current_task() in merged_tasks:
                if not query_yes_no(
                        "Task {} was already merged. Are you sure you want to continue?".format(current_task()), None):
                    print("Task not merged")
                    exit(1)

            gitlab_repo_name = "{}-{}-{}".format(group_number, first_name, last_name)

            try:
                gitlab_repo_name = config['gitlab_repo_name']
            except KeyError:
                pass

            gl = gitlab.Gitlab("https://gitlab.com", private_token=gitlab_token)
            gl.auth()

            tpcc_project = gl.projects.get(gitlab_repo_user + '/' + gitlab_repo_name)

            assignee = gl.users.list(username=assignee_username)[0]

            try:
                do_tests = config['test_before_merge']
            except KeyError:
                print('Key test_before_merge not found in configuration file. Assuming true')
                do_tests = True

            if do_tests and not is_theoretical_task(current_task()) and args.test:
                TestAction.run_tests('all')

            tpcc_project.mergerequests.create({
                'source_branch': current_task(),
                'target_branch': 'master',
                'title': '[{}] [{}] {} {}'.format(
                    group_number,
                    current_task(),
                    first_name,
                    last_name
                ),
                'labels': [group_number, 'HW-{}'.format(current_task()[0])],
                'assignee_id': assignee.id
            })
        except Exception as e:
            print(e, file=sys.stderr)
            traceback.print_exc()
            exit(1)

        merged_tasks.append(current_task())




def update_action(args=None):
    run(['git', 'pull'], cwd=TPCC_REPO,
        stdout=DEFAULT_OUTPUT,
        stderr=DEFAULT_ERROR)

def main():
    try:
        parser = argparse.ArgumentParser(prog='tpcc')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose')

        subparsers = parser.add_subparsers(title='Actions', dest='action')

        common_handlers = {}
        task_handlers = {}

        SetTaskAction.add_parser(subparsers, common_handlers)
        add_parser(subparsers, 'status', 'Print current task', common_handlers, status_action)
        add_parser(subparsers, 'config', 'Output current config', common_handlers, config_action)
        add_parser(subparsers, 'build', 'Run cmake for current task', task_handlers, build_action)
        add_parser(subparsers, 'clean', 'Clean current task build directory', task_handlers, clean_action)
        TestAction.add_parser(subparsers, task_handlers)
        add_parser(subparsers, 'style', 'Run clang-format on solution file', task_handlers, style_action)
        CommitTaskAction.add_parser(subparsers, task_handlers)
        GitlabMergeAction.add_parser(subparsers, task_handlers)
        add_parser(subparsers, 'pull', 'Pull from tpcc-course-2018 repository', common_handlers, update_action)
        add_parser(subparsers, 'update', 'Pull from tpcc-course-2018 repository', common_handlers, update_action)

        # process command line arguments
        args = parser.parse_args()

        if args.verbose:
            global DEFAULT_ERROR
            DEFAULT_ERROR = None

        if args.action in common_handlers:
            common_handlers[args.action](args)
        else:
            checkout_to_current_task()
            if current_task() == '':
                logger.error('No task selected. Specify current task using\n\ttpcc task <task_name>')

            if args.action in task_handlers:
                task_handlers[args.action](args)

        # some handy exception handling
        # to show nicely formatted and detailed enough
        # error messages to user
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("exiting on user request", file=sys.stderr)
        exit_code = 0
    except Exception as e:
        print(e, file=sys.stderr)
        traceback.print_exc()
        exit_code = 1
    else:
        exit_code = 0
    json.dump(state, open(STATE_PATH, 'w'))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

