# travis related functions (copied from https://github.com/travis-ci/travis-build/blob/master/lib/travis/build/templates/header.sh)
export ANSI_RED="\033[31;1m"
export ANSI_GREEN="\033[32;1m"
export ANSI_BLUE="\033[34;1m"
export ANSI_RESET="\033[0m"
export ANSI_CLEAR="\033[0K"

function travis_time_start {
    set +x
    TRAVIS_START_TIME=$(date +%s%N)
    TRAVIS_TIME_ID=$(printf "%x" $TRAVIS_START_TIME)
    TRAVIS_FOLD_NAME=$1

    if [[ "${GITHUB_ACTIONS}" == "true" ]]; then
        echo "::group::$TRAVIS_FOLD_NAME"
    else
        echo -e "${ANSI_CLEAR}traivs_fold:start:$TRAVIS_FOLD_NAME"
        echo -e "${ANSI_CLEAR}traivs_time:start:$TRAVIS_TIME_ID${ANSI_BLUE}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>${ANSI_RESET}"
    fi
    set -x
}
export -f travis_time_start

function travis_time_end {
    set +x
    _COLOR=${1:-32}
    TRAVIS_END_TIME=$(date +%s%N)
    TIME_ELAPSED_SECONDS=$(( ($TRAVIS_END_TIME - $TRAVIS_START_TIME)/1000000000 ))
    if [[ "${GITHUB_ACTIONS}" == "true" ]]; then
        echo "::endgroup::"
    else
        echo -e "traivs_time:end:$TRAVIS_TIME_ID:start=$TRAVIS_START_TIME,finish=$TRAVIS_END_TIME,duration=$(($TRAVIS_END_TIME - $TRAVIS_START_TIME))\n${ANSI_CLEAR}"
        echo -e "traivs_fold:end:$TRAVIS_FOLD_NAME\e[${_COLOR}m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<${ANSI_RESET}"
    fi
    echo -e "${ANSI_CLEAR}\e[${_COLOR}mFunction $TRAVIS_FOLD_NAME takes $(( $TIME_ELAPSED_SECONDS / 60 )) min $(( $TIME_ELAPSED_SECONDS % 60 )) sec${ANSI_RESET}"
}
export -f travis_time_end

function travis_wait {
  set +x
  local timeout=$1

  if [[ $timeout =~ ^[0-9]+$ ]]; then
    # looks like an integer, so we assume it's a timeout
    shift
  else
    # default value
    timeout=20
  fi

  local cmd="$@"
  local log_file=travis_wait_$$.log

  $cmd &>$log_file &
  local cmd_pid=$!

  travis_jigger $! $timeout $cmd &
  local jigger_pid=$!
  local result

  {
    wait $cmd_pid 2>/dev/null
    result=$?
    ps -p$jigger_pid &>/dev/null && kill $jigger_pid
  }

  if [ $result -eq 0 ]; then
    echo -e "\n${ANSI_GREEN}The command $cmd exited with $result.${ANSI_RESET}"
  else
    echo -e "\n${ANSI_RED}The command $cmd exited with $result.${ANSI_RESET}"
  fi

  echo -e "\n${ANSI_GREEN}Log:${ANSI_RESET}\n"
  cat $log_file

  set -x
  return $result
}
export -f travis_wait

function travis_jigger {
  # helper method for travis_wait()
  local cmd_pid=$1
  shift
  local timeout=$1 # in minutes
  shift
  local count=0

  # clear the line
  echo -e "\n"

  while [ $count -lt $timeout ]; do
    count=$(($count + 1))
    echo -ne "Still running ($count of $timeout): $@\r"
    sleep 60
  done

  echo -e "\n${ANSI_RED}Timeout (${timeout} minutes) reached. Terminating \"$@\"${ANSI_RESET}\n"
  kill -9 $cmd_pid
}
export -f travis_jigger

# end of travis related functions

