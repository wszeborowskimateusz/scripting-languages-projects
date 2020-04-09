#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

module = Extension( "simple_graphs", sources = ["main.c"] )

setup( name = "simple_graphs", ext_modules = [module] )
