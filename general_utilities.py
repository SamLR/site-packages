from math import floor, sqrt

def wait_to_quit():
    print "Press ctrl+C to stop"
    try:
        while(True):
            pass
    except KeyboardInterrupt, e:
        print "bye bye"
        return


def get_quantised_width_height(area):
    """
    Returns the width and height of the rectangle closest to a square of 
    given area.
    
    The width is incremented first e.g. for an area '5' returns (3,2)
    """
    y = floor(sqrt(area) + 0.49)
    x = round(sqrt(area) + 0.49)
    return int(x),int(y)


def test_get_quantised_width_height():
    expect = {1:(1,1), 2:(2,1), 3:(2,2), 4:(2,2), 5:(3,2), 6:(3,2), 7:(3,3)}
    print "Testing: get_quantised_width_height"
    print "Type test"
    a,b = get_quantised_width_height(9)
    print "Expect x & y to be ints: ",type(a), type(b)
    passed = True if type(a) == type(b) == int else False
    print "Passed\n" if passed else "Failed\n"
    if not passed: return
    for area, (x,y) in expect.items():
        print "Area=%i\nExpect: %ix%i"%(area, x, y)
        res_x, res_y = get_quantised_width_height(area)
        print "%7s %ix%i"%("got:", res_x, res_y)
        if (x,y) != (res_x, res_y):
            print "failed"
            return
        else:
            print "passed"
    print "get_quantised_width_height passed all tests"

if __name__=='__main__':
    test_get_quantised_width_height()
    print "\n This is wait_to_quit:"
    wait_to_quit()