#!/usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-

from setuptools import Command 
from setuptools._distutils import errors 
from setuptools._distutils import log
import os
import os.path
import setuptools
import shutil
import subprocess


class BuildIDL(Command):
    description = 'generate Python stubs from the IDL files'
    user_options = [
        ('omniidl=', 'o', 'omniidl compiler executable'),
        ('stubs-dir=', 's', 'directory to generate stubs in'),
        ('idl-dir=', 'i', 'directory to place IDL files in'),
        ]

    def initialize_options(self):
        self.omniidl = None
        self.stubs_dir = None
        self.idl_dir = None
        self.build_lib = None

    def finalize_options(self):
        if not self.omniidl:
            self.omniidl = 'omniidl'
        if not self.stubs_dir:
            self.set_undefined_options('build', ('build_base', 'stubs_dir'))
            self.stubs_dir = os.path.join(self.stubs_dir, 'stubs')
        if not self.idl_dir:
            self.set_undefined_options('build', ('build_base', 'idl_dir'))
            self.idl_dir = os.path.join(self.idl_dir, 'idl')
        self.idl_src_dir = os.path.join(os.getcwd(), 'idl')
        self.set_undefined_options('build', ('build_lib', 'build_lib'))

    def compile_one_idl(self, idl_f):
        outdir_param = '-C' + self.stubs_dir
        pkg_param = '-Wbpackage=rtctree.rtc'
        idl_path_param = '-Iidl'
        p = subprocess.Popen([self.omniidl, '-bpython', idl_path_param,
                              outdir_param, pkg_param, idl_f],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise errors.DistutilsExecError(
                'Failed to compile IDL file {}\nStdout:\n{}\n---\nStderr:\n'
                '{}'.format(idl_f, stdout, stderr))

    def compile_idl(self):
        log.info('Generating Python stubs from IDL files')
        self.mkpath(self.stubs_dir)
        idl_files = [os.path.join(self.idl_src_dir, f)
                     for f in os.listdir(self.idl_src_dir)
                     if os.path.splitext(f)[1] == '.idl']
        for f in idl_files:
            self.compile_one_idl(f)

    def move_stubs(self):
        stub_dest = os.path.join(self.build_lib, 'rtctree', 'rtc')
        log.info('Moving stubs to package directory {}'.format(stub_dest))
        self.copy_tree(os.path.join(self.stubs_dir, 'rtctree', 'rtc'),
                       stub_dest)

    def copy_idl(self):
        log.info('Copying IDL files')
        self.mkpath(self.idl_dir)
        idl_files = [os.path.join(self.idl_src_dir, f)
                     for f in os.listdir(self.idl_src_dir)
                     if os.path.splitext(f)[1] == '.idl']
        for f in idl_files:
            shutil.copy(f, self.idl_dir)

    def run(self):
        self.compile_idl()
        self.move_stubs()
        self.copy_idl()


class InstallIDL(Command):
    description = 'install the Python stubs generated from IDL files'
    user_options = [
        ('install-dir=', 'd', 'directory to install stubs to'),
        ('build-dir=', 'b', 'build directory (where to install from'),
        ('force', 'f', 'force installation (overwrite existing files)'),
        ('skip-build', None, 'skip the build steps'),
        ]
    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.install_dir = None
        self.build_dir = None
        self.force = None
        self.skip_build = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_dir'))
        self.set_undefined_options('install', ('install_lib', 'install_dir'),
                                   ('force', 'force'),
                                   ('skip_build', 'skip_build'))

    def run(self):
        if not self.skip_build:
            self.run_command('build_idl')
        # Copy the IDL files to rtctree/data/idl
        self.outfiles = self.copy_tree(
                os.path.join(self.build_dir, 'idl'),
                os.path.join(self.install_dir, 'rtctree', 'data', 'idl'))

    def get_outputs(self):
        return self.outfiles or []


# vim: set expandtab tabstop=8 shiftwidth=4 softtabstop=4 textwidth=79
