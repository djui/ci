#!/bin/sh

basedir=${1:-.}

# Optimization:
# Courtesy: https://github.com/cockroachdb/cockroach/blob/c6e4a65d7de66560877b1d42f9f8e62ba9702c01/circle.yml
# Set access and modification time of all files to arbitrary time in the past.
# Then set access and modification time of all files to their commit time.
find "$basedir" -exec touch -t 200001010000 {} \;

for x in $(git ls-tree --full-tree --name-only -r HEAD "$basedir"); do
    ## Alternative approach using RFC-2822 timestamps. Likely not needed.
    #touch -t $(date -d "$(git log -1 --format=%cd --date=rfc2822 "$x")" +%y%m%d%H%M.%S) "$x"
    touch -t $(date -d "$(git log -1 --format=%ci "$x")" +%y%m%d%H%M.%S) "$x"
done
