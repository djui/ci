# CI

CI is a set of tools that can make continuous integration toolchain faster.

# Tools

## git-submodule-cache.py

Creates a cache of submodules from which a repository will clone from, removing
latency from going over the network to fetch files and also to check if they are
state.


## update-ctime.sh

Git uses the checkout time to set the timestamp of files and directories instead
of their commit time. This tool updates the timestamp of all files to their
commit time. This optimizes docker builds and other tools that rely on unchanged
files are visible as unchanged.
