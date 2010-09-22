Lightweight Aspect-oriented Module for Python
=============================================
Hooks advice to a function or method.

advise() is a decorator that takes a set of functions or methods and injects
the decorated function in their place. There is no concept of before/after
callbacks. Instead, the intercepting function is responsible for calling (or
not) the intercepted function.

The "classic" logging example::

  class A(object):
    def a_function(self):
      print 'a_function()'

  @advise(A.a_function)
  def logit(on, next, *args, **kwargs):
    logging.debug('%r.%r(%r, %r)', on, next, args, kwargs)
    return next(*args, **kwargs)
