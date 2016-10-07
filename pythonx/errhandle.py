# -*- coding: utf-8 -*-
import sys

def foo(exctype, value, tb):
	print 'My Error Information'
	print 'Type:', exctype
	print 'Value:', value
	print 'Traceback:', tb

sys.excepthook = foo

