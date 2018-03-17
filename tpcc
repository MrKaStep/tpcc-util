#!venv/bin/python3

import argparse
import subprocess
import gitlab
import config
import os
from shutil import which
from git import Repo
import sys


def update_main_repo():
    tpcc_repo = Repo.init(os.path.join(config.path_to_repos, "tpcc-course-2018"))
    origin = tpcc_repo.remote('origin')
    origin.pull()
    # print("Reading from tpcc-course-2018:")
    # subprocess.run(["git", "pull"], cwd=os.path.join(config.path_to_repos, "tpcc-course-2018"))


def build(task_name):
    build_path = os.path.join(
        config.path_to_repos,
        'tpcc-course-2018',
        'tasks',
        task_name,
        'build'
    )

    solution_path = os.path.join(
        config.path_to_repos,
        'solutions',
        task_name
    )

    if not os.path.isdir(build_path):
        raise FileNotFoundError("Incorrect task name")

    if not os.path.isdir(solution_path):
        raise FileNotFoundError("Solution directory for task {} does not exist".format(task_name))

    if "solution.hpp" not in os.listdir(solution_path):
        raise FileNotFoundError("{}/solution.hpp does not exist".format(task_name))

    clang_compiler = which("clang++-5.0")

    if clang_compiler is None:
        print("clang++-5.0 not found, trying clang++")
        clang_compiler = which("clang++")
        if clang_compiler is None:
            raise FileNotFoundError("No suitable clang compiler")

    subprocess.run(['cmake', '..', '-DCMAKE_CXX_COMPILER={}'.format(clang_compiler)],
                   cwd=build_path, check=True)

    subprocess.run(['make', 'run'], cwd=build_path, check=True)


def push_to_remote(task_name):
    solution_repo = Repo.init(os.path.join(config.path_to_repos, 'solutions'))
    solution_repo.git.checkout('master')

    branch = solution_repo.create_head(task_name)
    origin = solution_repo.remote('origin')

    task_path = os.path.join(config.path_to_repos, 'solutions', task_name)

    if not os.path.isdir(task_path):
        raise FileNotFoundError("Directory {} not found".format(task_name))

    solution_repo.git.checkout(task_name)
    solution_repo.git.add(task_path)
    try:
        solution_repo.git.commit(task_path, m='{} task solution added'.format(task_name))
    except:
        pass
    origin.push(task_name)

    solution_repo.git.checkout('master')


def create_merge_request(task_name):
    gl = gitlab.Gitlab("https://gitlab.com", private_token=config.private_token)
    gl.auth()

    tpcc_project = gl.projects.get('tpcc-course-2018/{}-{}-{}'.format(
        config.group_number,
        config.first_name.lower(),
        config.last_name.lower()
    ))

    assignee = gl.users.list(username=config.assignee_username)[0]

    tpcc_project.mergerequests.create({
        'source_branch': task_name,
        'target_branch': 'master',
        'title': '[{}] [{}] {} {}'.format(
            config.group_number,
            task_name,
            config.first_name,
            config.last_name
        ),
        'labels': [config.group_number, 'HW-{}'.format(task_name[0])],
        'assignee_id': assignee.id
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("taskname")
    parser.add_argument("-u", "--update", dest="pull", help="pull from tpcc-course-2018 repository",
                        action="store_true")
    parser.add_argument("-b", "--build", dest="build", help="build and test your solution",
                        action="store_true")
    parser.add_argument("-p", "--push", dest="push", help="push to your solutions repository",
                        action="store_true")
    parser.add_argument("-m", "--merge", dest="mr", help="create merge request",
                        action="store_true")
    parser.add_argument("-a", "--all", dest="all", help="run full task cycle",
                        action="store_true")

    args = parser.parse_args()

    os.chdir(config.path_to_repos)

    if args.pull or args.all:
        update_main_repo()

    if args.build or args.all:
        try:
            build(args.taskname)
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            print("Build failed")
            print(e)
            # sys.exit(1)


    if args.push or args.all:
        push_to_remote(args.taskname)

    if args.mr or args.all:
        create_merge_request(args.taskname)
