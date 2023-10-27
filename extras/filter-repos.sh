#!/usr/bin/env bash

# script to filter using fzf the repositories by name

LOGGING_ENABLED=0

show_repo_information() {
  local name="$1"
  log "Showing information for repo: '$name'"
  jq -r ".[] | select(.name == \"$name\")" repositories.json
}

log() {
  [[ -z $LOGGING_ENABLED || $LOGGING_ENABLED -eq 0 ]] && return
  echo "$@"
}

# fzf_opts='--reverse --no-hscroll --no-multi --ansi --print-query --tiebreak=index'
fzf_opts='--reverse --no-hscroll --no-multi --ansi --print-query --tiebreak=index'
# ^ this needs `tput rmcup`, or does it?


query=""
while true; do
  fzf_header="Enter: show repo information"

  items=$(jq -r '.[] | .name' repositories.json)
  out=$(
  fzf $fzf_opts \
    --prompt="list> " \
    --query="$query" \
    --header="$fzf_header" \
    --expect="enter" \
    --delimiter=" " \
    --nth 1..2 \
    --bind="ctrl-o:toggle-preview" \
    --preview-window="right" \
    --preview="jq --color-output --raw-output '.[] | select(.name == \"{}\")' repositories.json" \
    --preview-label="Repository information from json file" \
    <<< "$items"
  )

  # 2: Error; 130: Interrupted with Ctrl-C or Esc
  (( $? % 128 == 2 )) && exit 1

  if [ $(wc -l <<< "$out") -lt 3 ]; then
    # this happens when there's no match on the fzf filtering, so no selected item
    log "WARNING: too few lines, no selected item"
    # log "out: '$out'"
    break
  fi

  # fzf out format with the current configuration:
  # out='query
  # key if/as defined on "expected"
  # selected line'

  query=$(head -1 <<< "$out")
  key=$(head -2 <<< "$out" | tail -1)
  line=$(tail -1 <<< "$out")  # this may be empty, check for $out length first

  log "out: '$out'"
  log "key: '$key'"
  log "line: '$line'"
  log "query: '$query'"

  if [[ -z $line ]]; then
    # (when) does this happen?
    log "WARNING: empty line"
    log "out: '$out'"
    continue
  fi

  case "$key" in
    enter)  [ -n "$line" ] && show_repo_information "${line}" && break ;;
  esac

done
