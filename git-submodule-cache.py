#!/usr/bin/env python

from __future__ import print_function
import argparse
import ConfigParser
import hashlib
import os
import StringIO
import subprocess
import sys


class Git():
    @staticmethod
    def parse_gitconfig(path):
        if not os.path.isfile(path):
            return {}
        with open(path) as f:
            c = ConfigParser.ConfigParser()
            c.readfp(StringIO.StringIO(f.read().replace('\t', '')))
            return dict([(s, dict(c.items(s))) for s in c.sections()])
        
    @staticmethod
    def fetch(args):
        subprocess.check_output(['git', 'fetch'] + args)

    @staticmethod
    def clone(args):
        subprocess.check_output(['git', 'clone'] + args)


class GitSubmoduleCache():
    def __init__(self, root='~/.gitcache', refresh=False):
        self.root = os.path.expanduser(root)

    def cache(self, url):
        target = os.path.join(self.root, GitSubmoduleCache.hash(url))
        if GitSubmoduleCache.is_cached(target):
            #Git.fetch(['--all'])
            pass
        else:
            Git.clone(['--mirror', url, target])
        return target

    @staticmethod
    def is_cached(path):
        return os.path.isdir(path)

    @staticmethod
    def hash(url):
        return hashlib.sha1(url).hexdigest()


def checkout_submodules(path, cache):
    """Recursively clone submodules from a local cache. If a submodule is not in the
    cache, it gets cloned first. This is an optimization for consecutive
    repository clones with many submodules. Note: This is meant only for a
    one-time checkout of code; submodules are not correct initialized and can't
    be updated."""
    gitmodules_path = os.path.join(path, '.gitmodules')
    gitmodules = Git.parse_gitconfig(gitmodules_path)
    branch = lambda b: ['--branch', b] if b else []
    
    for s in gitmodules.values():
        if s.get('ignore') or not s.get('path') or not s.get('url'):
            continue  # ignored or invalid
        #Git.clone(branch(s.get('branch')) +
        #          ['--reference', cache.cache(s.get('url')),
        #           '--dissociate',
        #           '--single-branch',
        #           '--depth', '1',
        #           s.get('url'),
        #           os.path.join(path, s.get('path'))])
        Git.clone(branch(s.get('branch')) +
                  ['--single-branch',
                   '--depth', '1',
                   'file://' + cache.cache(s.get('url')),
                   os.path.join(path, s.get('path'))])
        checkout_submodules(s.get('path'), cache)  # recurse


def main(args):
    try:
        cache = GitSubmoduleCache(os.path.expanduser(args.path), args.refresh)
        checkout_submodules(os.path.expanduser(args.dir), cache)
    except Exception as e:
        print(e)
    

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Git submodule cacher.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('dir', metavar='DIR', nargs='?', default='.', help='path to repo')
        parser.add_argument('-p', '--path', default='~/.gitcache', help='path to cache dir')
        parser.add_argument('-r', '--refresh', action='store_true', default=False, help='ensure cache is never stale')
        parser.add_argument('-v', '--verbose', action='count', default=0, help='set verbosity level')
        sys.exit(main(parser.parse_args()))
    except KeyboardInterrupt:
        sys.exit(1)
