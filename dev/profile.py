__author__ = 'acb'
import objgraph
import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno
def hi(s):
    return
    if objgraph.show_growth():
        print "----line:",s
        objgraph.show_most_common_types()
