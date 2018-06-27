################################################################################
# Copyright (c) 2013, Dougal J. Sutherland (dsutherl@cs.cmu.edu).
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Carnegie Mellon University nor the
#       names of the contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import errno
from functools import partial
import json
import os
import subprocess


################################################################################
# The following chunk of code for querying pkg-config is loosely based on code
# from the cffi package, which is licensed as follows:
#
#    The MIT License
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or
#    sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.

def _ask_pkg_config(lib, option, result_prefix='', sysroot=False, default=None):
    pkg_config = os.environ.get('PKG_CONFIG', 'pkg-config')
    try:
        output = subprocess.check_output([pkg_config, option, lib])
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    except subprocess.CalledProcessError:
        pass
    else:
        res = output.decode().strip().split()

        # '-I/usr/...' -> '/usr/...'
        for x in res:
            assert x.startswith(result_prefix)
        res = [x[len(result_prefix):] for x in res]

        if sysroot:
            sysroot = os.environ.get('PKG_CONFIG_SYSROOT_DIR', '')
        if sysroot:
            # old versions of pkg-config don't support this env var,
            # so here we emulate its effect if needed
            res = [path if path.startswith(sysroot) else sysroot + path
                   for path in res]

        return res
    return [] if default is None else default


def get_pkg_info(name):
    ask = partial(_ask_pkg_config, name)
    return {
        'libraries': ask('--libs-only-l', '-l', default=[name]),
        'include_dirs': ask('--cflags-only-I', '-I', sysroot=True),
        'library_dirs': ask('--libs-only-L', '-L', sysroot=True),
        'extra_compile_args': ask('--cflags-only-other'),
        'extra_link_args': ask('--libs-only-other'),
        'runtime_library_dirs': ask('--variable=libdir'),
    }


################################################################################
# Get FLANN info

_flann_info = None


def get_flann_info(flann_dir=None, use_cache=True):
    global _flann_info
    if _flann_info is not None and use_cache:
        return _flann_info

    if flann_dir is None:
        flann_dir = os.environ.get('FLANN_DIR')

    if flann_dir is None:
        pth = os.path.join(os.path.dirname(__file__), 'flann_config.json')
        try:
            with open(pth, 'r') as f:
                meta = json.load(f)
        except IOError:
            pass
        else:
            flann_dir = meta.get('FLANN_DIR')

    if flann_dir:
        pre = partial(os.path.join, flann_dir)
        lib_dirs = [pre('lib')]
        if os.path.isdir(pre('lib64')) and sys.maxsize > 2**32:
            lib_dirs.append(pre('lib64'))

        _flann_info = {
            'libraries': ['flann', 'flann_cpp'],
            'include_dirs': [pre('include')],
            'library_dirs': lib_dirs,
            'extra_compile_args': [],
            'extra_link_args': [],
            'runtime_library_dirs': lib_dirs,
        }
    else:
        _flann_info = get_pkg_info('flann')
        if _flann_info['libraries'] == ['flann_cpp']:
            import warnings
            warnings.warn("It looks like you're using an old version of FLANN "
                          "with a bug in its pkg-config settings. Trying to "
                          "work around this, but you'd be better off setting "
                          "FLANN_DIR as described in the README, or updating "
                          "to FLANN 1.9 or higher.")
            _flann_info['libraries'].insert(0, 'flann')

    if os.name == 'nt':
        _flann_info['runtime_library_dirs'] = []
        # flann_cpp.lib doesn't exist for some reason
        _flann_info['libraries'].remove('flann_cpp')

    return _flann_info
