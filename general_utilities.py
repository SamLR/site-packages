
def wait_to_quit():
    print "Press ctrl+C to stop"
    try:
        while(True):
            pass
    except KeyboardInterrupt, e:
        print "bye bye"
        return

  



