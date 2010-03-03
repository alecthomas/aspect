import sys
import types


def advise(*join_points):
    """Hook advice to a function or method.

    >>> def eat(lunch):
    ...   print 'eating', lunch

    >>> @advise(eat)
    ... def replace_sandwich(next, lunch):
    ...   if lunch == 'sandwich':
    ...     print 'delicious sandwich!'
    ...     return next('dirt')
    ...   else:
    ...     return next(lunch)

    >>> eat('soup')
    eating soup

    >>> eat('sandwich')
    delicious sandwich!
    eating dirt

    >>> class Eater(object):
    ...   def eat(self):
    ...     print 'tastes like identity!'
    ...   @classmethod
    ...   def eat_class(cls):
    ...     print 'let them eat cake!'
    ...   @staticmethod
    ...   def eat_static():
    ...     print 'mmm, static cling'

    Multiple functions can be advised at the same time, including classmethods
    and staticmethods:

    >>> @advise(Eater.eat, Eater.eat_class, Eater.eat_static)
    ... def delicious(next):
    ...   print 'delicious!'
    ...   return next()

    Normal method:

    >>> Eater().eat()
    delicious!
    tastes like identity!

    Class method:

    >>> Eater.eat_class()
    delicious!
    let them eat cake!

    Static method:

    >>> Eater.eat_static()
    delicious!
    mmm, static cling
    """
    hook = []
    def hook_advice(join_point):
        def wrapper(*args, **kwargs):
            return hook[0](on, join_point, *args, **kwargs)

        # Either a normal method or a class method
        if type(join_point) is types.MethodType:
            # Class method
            if join_point.im_self:
                on = join_point.im_self
                @classmethod
                def wrapper(cls, *args, **kwargs):
                    return hook[0](cls, join_point, *args, **kwargs)
            else:
                # Normal method, curry "self"
                def wrapper(self, *args, **kwargs):
                    return hook[0](self,
                                   lambda *a, **kw: join_point(self, *a, **kw),
                                   *args, **kwargs)
                on = join_point.im_class
        else:
            # Static method or global function
            on = sys.modules[join_point.__module__]
            caller_globals = join_point.func_globals
            name = join_point.__name__
            # Global function
            if caller_globals.get(name) is join_point:
                caller_globals[name] = wrapper
            else:
                # Probably a staticmethod, try to find the attached class
                for on in caller_globals.values():
                    if getattr(on, name, None) is join_point:
                        wrapper = staticmethod(wrapper)
                        break
                else:
                    raise ValueError('%s is not a global scope function and '
                                     'could not be found in top-level classes'
                                     % name)
        name = join_point.__name__
        setattr(on, name, wrapper)

    for join_point in join_points:
        hook_advice(join_point)

    def add_hook(func):
        hook.append(func)
        return func
    return add_hook


if __name__ == '__main__':
    import doctest
    doctest.testmod()
