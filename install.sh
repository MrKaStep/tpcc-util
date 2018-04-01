#!/usr/bin/env bash

#apt-get install python3-venv
/usr/bin/python3 -m venv venv;
./venv/bin/pip3 install -r requirements.txt

mkdir ${HOME}/.tpcc
echo '
{
        "gitlab_token": "<gitlab_token>",
        "path_to_repos": "<path_to_repos>",
        "course_repo_name": "tpcc-course-2018",
        "group_number": "<group_number>",
        "first_name": "<first_name>",
        "last_name": "<last_name>",
        "assignee_username": "<assignee_username>",
        "gitlab_repo_user": "tpcc-course-2018",
        "test_before_merge": true
}
' > ${HOME}/.tpcc/config.json

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

#mkdir -p ${HOME}/.local/bin

ln -s ${DIR}/tpcc /usr/bin/tpcc
