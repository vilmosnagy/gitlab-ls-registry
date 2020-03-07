#!/usr/bin/env bash

for f in /docker-entrypoint.d/*; do
  case "$f" in
    *.sh)
      if [ -x "$f" ]; then
        echo "$0: running $f"
        "$f"
      else
        echo "$0: sourcing $f"
        . "$f"
      fi
      ;;
  esac
  echo
done

echo $CMD
if [[ "$CMD" = "delete" ]]; then
    python /opt/src/delete_images.py
fi
