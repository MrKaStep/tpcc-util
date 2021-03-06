#!/usr/bin/env bash

#apt-get install python3-venv

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     sudo apt-get install python3-venv && /usr/bin/python3 -m venv venv;;
    Darwin*)    pip3 install virtualenv && virtualenv -p python3 venv;;
esac

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

${DIR}/venv/bin/pip3 install -r requirements.txt

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

if ! [ -d ${HOME}/bin ]
then
    mkdir ${HOME}/bin
    if [ -f ${HOME}/.bash_profile ]
    then
        echo "PATH=${HOME}/bin:\$PATH" >> ${HOME}/.bash_profile
    elif [ -f ${HOME}/.bashrc ]
    then
        echo "PATH=${HOME}/bin:\$PATH" >> ${HOME}/.bashrc
    else
        echo "PATH=${HOME}/bin:\$PATH" >> ${HOME}/.profile
    fi
fi

ln -s ${DIR}/tpcc ${HOME}/bin/tpcc
