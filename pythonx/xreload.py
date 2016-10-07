import types
import inspect
import __builtin__

def xreload(mod):
	olddict=mod.__dict__.copy()
	__builtin__.reload(mod)
	newdict=mod.__dict__.copy()
	_dict=mod.__dict__
	oldnames = set(olddict)
	newnames = set(newdict)
	for name in newnames:
		newobj=newdict[name]
		oldobj=olddict.get(name,newobj)
		_dict[name] = _update(oldobj, newobj)
	for name in set(olddict)-set(newdict):
		del _dict[name] 
	return mod

def _update(oldobj, newobj):
	if oldobj is newobj:
		return newobj
	if type(oldobj) is not type(newobj):
		return newobj
	if hasattr(newobj, "__reload_update__"):
		# Provide a hook for updating
		return newobj.__reload_update__(oldobj)
	if inspect.isclass(newobj):
		return _update_class(oldobj, newobj)
	elif inspect.isfunction(newobj):
		return _update_function(oldobj, newobj)
	elif isinstance(newobj, types.MethodType):
		return _update_method(oldobj, newobj)
	elif isinstance(newobj, classmethod):
		return _update_classmethod(oldobj, newobj)
	elif isinstance(newobj, staticmethod):
		return _update_staticmethod(oldobj, newobj)
	return newobj 

def _update_function(oldfunc, newfunc):
	"""Update a function object."""
	oldfunc.__doc__ = newfunc.__doc__
	oldfunc.__dict__.update(newfunc.__dict__)
	oldfunc.__code__ = newfunc.__code__
	oldfunc.__defaults__ = newfunc.__defaults__
	return oldfunc


def _update_method(oldmeth, newmeth):
	"""Update a method object."""
	# XXX What if im_func is not a function?
	_update(oldmeth.im_func, newmeth.im_func)
	return oldmeth


def _update_class(oldclass, newclass):
	"""Update a class object."""
	olddict = oldclass.__dict__
	newdict = newclass.__dict__
	oldnames = set(olddict)
	newnames = set(newdict)
	for name in newnames - oldnames:
		setattr(oldclass, name, newdict[name])
	for name in oldnames - newnames:
		delattr(oldclass, name)
	for name in oldnames & newnames - {"__dict__", "__doc__"}:
		setattr(oldclass, name,  _update(olddict[name], newdict[name]))
	return oldclass


def _update_classmethod(oldcm, newcm):
	"""Update a classmethod update."""
	# While we can't modify the classmethod object itself (it has no
	# mutable attributes), we *can* extract the underlying function
	# (by calling __get__(), which returns a method object) and update
	# it in-place.  We don't have the class available to pass to
	# __get__() but any object except None will do.
	_update(oldcm.__get__(0), newcm.__get__(0))
	return newcm


def _update_staticmethod(oldsm, newsm):
	"""Update a staticmethod update."""
	# While we can't modify the staticmethod object itself (it has no
	# mutable attributes), we *can* extract the underlying function
	# (by calling __get__(), which returns it) and update it in-place.
	# We don't have the class available to pass to __get__() but any
	# object except None will do.
	_update(oldsm.__get__(0), newsm.__get__(0))
	return newsm
