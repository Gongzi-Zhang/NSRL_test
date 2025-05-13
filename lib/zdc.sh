#!/bin/bash

script=$(basename -- ${BASH_SOURCE[0]})
if [ -z "${ZDCROOT+x}" ]; then                                                 
    source  ${script}/../setup.sh                                          
fi  

export SSH_AUTH_SOCK=/run/user/1000/keyring/ssh

# IO
black="\033[30;20m"
red="\033[31;20m"
green="\033[32;20m"
yellow="\033[33;20m"
blue="\033[34;20m"
bold_red="\033[31;1m"
reset="\033[0m"

declare -A color=( \
    [debug]=$blue \
    [info]=$green \
    [warning]=$yellow \
    [error]=$red \
    [fatal]=$bold_red \
)

logger()
{
    level=$1; shift
    echo -e "($script:$LINENO) ${color[$level]}${level^^}$reset -" $@
}

logger_test()
{
    logger debug "debug"
    logger info "info"
    logger warning "warning"
    logger error "error"
    logger fatal "fatal"
}

# File
getFile() 
{
    for dir in "." "${ZDCROOT}/data/" "${backupDir}/data/"; do
	f="${dir}/${1}"
	if [ -f "$f" ]; then
	    echo $f
	    break
	fi
    done
}
