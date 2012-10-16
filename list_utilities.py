#!/usr/bin/env python
# encoding: utf-8
"""
list_utils.py

Created by Sam Cook on 2012-01-04.

A collection of useful utilities for use with lists and other list-like
objects (i.e. tuples and dictionaries)
"""

def add_as_sub_dict(parent_dict, key, subkey, subval):
    """
    If key exists in parent_dict add the pair subkey:subval to it, otherwise
    make key's value a dictionary containing that pair.
    
    Will raise a TypeError if key exists but is not indexable.
    """
    if not key in parent_dict.keys():
        parent_dict[key] = {subkey:subval}
    else:
        parent_dict[key][subkey] = subval


def test_add_as_sub_dict():
    D = {}
    D_expected = {'a':{'b':'c'}}
    add_as_sub_dict(D,'a', 'b', 'c')
    print "D:  ",D
    print "D_e:", D_expected
    print "D==D_expected?", D==D_expected,"\n"
    D_expected2 = {'a':{'b':'c', 'd':'e'}}
    add_as_sub_dict(D,'a', 'd', 'e')
    print "D:  ",D
    print "D_e:", D_expected2
    print "D==D_expected?", D==D_expected2,"\n"
    try:
        add_as_sub_dict(D['a'],'d', 'fail', 'fail')
    except TypeError, e:
        print "This should cause a type error"
        print "Attempting D['a']['d']['fail] = 'fail' but 'd' is a string"
        print e


def create_sub_dicts_from_keys(dict, keysplit_function):
    """
    Use the keysplit_function to extract (key, sub-key) pairs 
    and return a copy of the dictionary split with that structure
    
    Example:
    {'a_1':1, 'a_2':2, 'b_1':3, 'b_2':4}
            -> {'a':{'1':1,'2':2}, 'b':{'1':3,'2':4}}
    keysplit_function = lambda x: (x.split('_')[0], x.split('_')[1])
    """
    res = {}
    for initial_key in dict:
        key, sub_key = keysplit_function(initial_key)
        value = dict[initial_key]
        if key in res:
            res[key][sub_key] = value
        else:
            res[key] = {sub_key:value}
    return res
    


def test_create_sub_dicts_from_keys():
    test = {'a_1':1, 'a_2':2, 'b_1':3, 'b_2':4}
    expect = {'a':{'1':1,'2':2}, 'b':{'1':3,'2':4}}
    print 'testing create_sub_dicts_from_keys'
    keysplit_func = lambda x: (x.split('_')[0], x.split('_')[1])
    res = create_sub_dicts_from_keys(test, keysplit_func)
    print 'expect: ', expect
    print 'got:    ', res
    print 'passed' if expect==res else 'failed'
    print 'create_sub_dicts_from_keys passed all tests \n'


def traverse(obj, pmode=False, level=0):
    """
    Traverses an object yielding its contents. Strings are not traversed.
    For dictionaries the key is first returned then the contents at that key.
    Level is a depth counter. 
    A 'True' value of pmode will yield both the value and the level 
    
    Based on the solution given by Jeremy Banks, here: http://stackoverflow.com/questions/6290105/traversing-a-list-tree-and-get-the-typeitem-list-with-same-structure-in-pyth#6290211
    """
    if hasattr(obj, 'keys'):
        for val in obj:
            yield val if not pmode else ('{'+str(val), level)
            level += 1
            for subval in traverse(obj[val], pmode, level):
                yield subval
            level -= 1    
            if pmode: yield ('}', level)
    elif hasattr(obj, '__iter__'):
        for val in obj:
            level += 1
            for subval in traverse(val, pmode, level):
                yield subval
            # yield subval, level 
            level -= 1 
    else:
        yield obj if not pmode else (obj, level)


def printTraverse(obj,spacer='.'):
    """
    prints the contentss of obj in a nested manner
    """
    for i in traverse(obj, pmode=True): print "%s%s"%(spacer*i[1], i[0])


def saveTraverse(obj,file,spacer='.',header=''):
    """
    Save the contents of obj to the file
    """
    header += "\n"
    file.write(header)
    for i in traverse(obj, pmode=True): file.write("%s%s\n"%(spacer*i[1], i[0]))


def test_traverse():
    """tests the traverse method"""
    test1 = {'a': 1, 'b':2, 'c':(2, 3, 4, 5), 'd':"string", 'e':{'test':6, 'depth':7}}
    print 'test 1: traverse(test1)'
    print 'test1: ', test1
    output = []
    expected = ['a', 1, 'b', 2, 'c', 2, 3, 4, 5, 'd', 'string', 'e', 'test', 6, 'depth', 7]
    for i in traverse(test1): output.append(i)
    output.sort()
    expected.sort()
    print 'expect:',expected
    print 'got:   ',output
    print "passed\n" if (output == expected) else "fail\n"
    print 'test 2 printTraverse(test1,\'-\')'
    printTraverse(test1,'-')


def main():
    print 'test_traverse()'
    test_traverse()
    print '\ntest_add_as_sub_dict()'
    test_add_as_sub_dict()
    print '\ntest_create_sub_dicts_from_keys()'
    test_create_sub_dicts_from_keys()
    print "\nAll tests finished"


if __name__ == '__main__':
    main()

