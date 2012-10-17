#!/usr/bin/env python
# encoding: utf-8
"""
utilities.py

Created by Sam Cook on 2012-07-25.

Generally useful functions for dealing with ROOT objects
"""

from ROOT import gROOT, TFile, TTree, TBranch, TCanvas, TLegend, \
                 TH1D, TH2D, TH3D

from general_utilities import get_quantised_width_height, \
                                increment_counter_attribute

from list_utilities import get_sorted_dict_keys

from sys import maxint

class ROOTException(Exception):
    pass


class Branch(object):
    """Represents a branch of a TTree, but also local stores the associated data"""
    # TODO make this an iterable object so we can easily loop over all entries
    def __init__(self, branch_ptr, data_object):
        self.ptr = branch_ptr
        self.data = data_object
    
    def __getitem__(self, key):
        return self.data.__getattribute__(key)
    
    def __getattr__(self, name):
        return self.ptr.__getattribute__(name)
    


def get_branch(tree, branch_name, data_class):
    """
    Gets a branch from a ROOT TTree and returns it as a useful object
    data_class must be a callable object that ROOT can write into
    """
    branch_ptr = tree.GetBranch(branch_name)
    branch_data = data_class()
    branch_ptr.SetAddress(branch_data)
    return Branch(branch_ptr, branch_data)


def get_struct(struct_fmt, struct_name):
    """
    Imports a named C struct with members given in struct comp at global scope.
    
    struct_fmt should be a string containing valid C defining the member
    variables of the struct all lines should end with a ';'
    """
    struct = "struct %s{%s};"%(struct_name, struct_fmt)
    # create the struct in CINT
    gROOT.ProcessLine(struct)
    # because we don't know the name of the struct we need to be able to 
    # access the entire ROOT module and use getattr to extract it dynamically
    tmp = __import__("ROOT")
    return tmp.__getattr__(struct_name)
    


def make_hist(name, mins=0, maxs=100, titles=None, bins=None, dim=1, des=None):
    """
    Make a named ROOT histogram. 
    
    Mins, maxs and bins can be supplied either as a single number to be 
    used for all axis, an indexable object (indexes: 0,1,2). If not supplied
    the defaults of 0, 100 and min-max (of that axis) will be used.
    
    If not supplied the number of bins per axis will be the difference 
    between the minimum and maximum (or 10 if the difference is less than 1)
    
    Titles will be set if supplied and are assumed be in the order (x,y,z)
    """
    dim = int(dim)
    if dim not in (1,2,3):
        raise ROOTException("dim must between 1 & 3")
    
    description = des if des else name
    
    # make the argument list
    args = [name, description,]
    for d in range(dim):
        t_min = mins if not hasattr(mins, '__len__') else mins[d]
        t_max = maxs if not hasattr(maxs, '__len__') else maxs[d]
        if hasattr(bins, '__len__'):
            t_bin = bins[d]
        elif bins:
            t_bin = bins
        else:
            t_bin = int(t_max - t_min) if int(t_max - t_min) > 1 else 1
        if (t_min>t_max): raise ROOTException("min > max!")
        args += [t_bin, t_min, t_max]
    
    if dim == 1:
        res = TH1D(*args)
    elif dim == 2:
        res = TH2D(*args)
    elif dim == 3:
        res = TH3D(*args)
        
    # Checking titles exists stops len raising an error if it doesn't 
    if titles and len(titles) >= 1: res.GetXaxis().SetTitle(titles[0])
    if titles and len(titles) >= 2: res.GetYaxis().SetTitle(titles[1])
    if titles and len(titles) >= 3: res.GetZaxis().SetTitle(titles[2])
    
    return res


def test_make_hist():
    from time import sleep
    t = []
    sleep_time = 1.5
    mins = (-50, -150, -250)
    maxs = (50, 150, 250)
    bins = (10, 5, 20)
    fills = ((1,), (1,2), (1,2,3))
    titles = ("x", "y", "z")
    draw_opt = ("", "CONTZ", "BOX")
    can = make_canvas("n", 2, 2)
    for i in range(3):
        can.cd(i+1)
        t.append( make_hist("h2_"+str(i), mins, maxs, titles,bins, dim=i+1))
        t[i].Fill(*fills[i])
        t[i].Draw(draw_opt[i])
    
    try:
        make_hist("h_fail", dim = 42)
    except ROOTException, e:
        print e, "Hooray if you see this!"
    
    try:
        make_hist("h_fail2", mins=42, maxs=2)
    except ROOTException, e:
        print e, "Hooray if you see this!"
    
    print "All tests passed (assuming visual inspection of histograms)"
    sleep (10)


def rebin_nbins(hist, n_bins, new_name=''):
    """
    Rebins a histogram to have n_bins, if new_name is not provided then 
    the original is modified. 
    NOTE: if n_bins is not an exact factor of the existing number of bins 
    then n_bins will be created and the excess (at the upper bin) will be 
    added to the overflow bin
    """
    # TODO make this aware of other dimensions
    if n_bins == 0:
        return hist 
    else:
        xmin = hist.GetXaxis().GetXmin()
        xmax = hist.GetXaxis().GetXmax()
        new_bin_width = int(float(xmax - xmin)/n_bins)
        if (hist.GetNbinsX()%new_bin_width != 0): 
            print "WARNING: unable to form an integer number of bins, \
            x max will be lowered"
        return rebin_bin_width(hist, new_bin_width, new_name)


def rebin_bin_width(hist, bin_width, new_name=''):
    # TODO make this aware of other dimensions
    if bin_width == 0: 
        return hist
    else:
        return hist.Rebin(bin_width, new_name)


def make_canvas(name, n_x=0, n_y=0, resize=False, _w=1436, _h=856):
    """
    Make a named canvas, optionally divide it into n_x and n_y pieces.
    If resize is true the canvas is made with specified width (_w) and
    height (_h), the default will maximise the canvas on a 1440x900 screen
    """
    name = str(name) # make sure we have a string
    canvas = TCanvas(name, name,_w,_h) if resize else TCanvas(name,name) 
    if n_x or n_y: canvas.Divide(n_x, n_y)
    return canvas


def get_contents_of_tfile_as_dict(folder, key_func=lambda x:x.GetName()):
    """
    Opens the named TFile and returns its contents as a dictionary.
    
    The dictionary's keys are determined by keyfunc (by default the 
    object's ROOT name).
    
    To maintain scope on the objects the TFile is also returned.
    """
    in_file = TFile(filename, "READ")
    res = {}
    for key in in_file.GetListOfKeys():
        obj = key.ReadObj()
        dict_key = key_func(obj)
        res[dict_key] = obj
    return res, in_tfile
    
    # Would have tried making a recurive version of this but there is no 
    # clear way to crawl a ROOT structure. This is due to there being
    # two base folder types: TFolder and TDirectory which are for 
    # structures in memory and files respectively. Both return true to 
    # 'isFolder()' but only TDirectory implments 'GetListOfKeys()', 
    # TFolder has no analogous method. In theory 'isA' should allow
    # direct testing but it is not clear how it is implemented.


def print_square_matrix(matrix, number_fmt="% 5.2e"):
    """
    Prints a square matrix (anything that has a 'GetNcols' method).
    
    Number format specifies how each value should be printed
    """
    dimension = matrix.GetNcols()
    fmt_string = (number_fmt + ' ') * dimension 
    for i in range (dimension):
        row = tuple([matrix[i][n] for n in range(dimension)])
        print fmt_string % row


def set_bin_val_er_label(hist, bin, val, er, bin_name):
    """
    Set the bin value, error and label.
    
    NB bin indexing starts from 1 (bin 0 is underflow).
    """
    hist.SetBinContent(bin, float(val))
    hist.SetBinError(bin, float(er))
    hist.GetXaxis().SetBinLabel(bin, str(bin_name))


def __find_x_in_hists(hists, initial_res, x_func, comp_func):
    """
    Helper function; apply x_func to all histograms in hists and
    then pass the result and return value to comp_func. If
    comp_func is true then the return value is updated.
    
    initial_res is the initial starting value for comp_func.
    """
    if hasattr(hists, 'keys'): hists = hists.values()
    res = initial_res
    for hist in hists:
        val = x_func(hist)
        if comp_func(res, val):
            res = val
    return res


def get_max_amongst_hists(hists):
    """
    Find the maximum value amongst hists
    """
    return __find_x_in_hists(hists, (-maxint - 1), 
                                lambda hist: hist.GetMaximum(),
                                lambda prev, this_val: prev < this_val)
        


def get_min_amongst_hists(hists):
    """
    Find the minimum value amongst hists
    """
    return __find_x_in_hists(hists, maxint,
                                lambda hist: hist.GetMinimum(),
                                lambda prev, this_val: prev > this_val)


def get_canvas_with_hists(hists, draw_opt='', canvas_name='c', set_y_zero=False, sort_args=[]):
    """
    Draws given histograms to a canvas. Assumes hists is either a dictionary
    of 
        <key>:<histogram> 
    pairs or a dictionary of 
        <key>:{<sub-key>:<sub histograms>} 
    pairs. In either case a single canvas will be divided into pads (1 per 
    key), and the histogram(s) associated with that key drawn to that pad.
    
    draw_opt are any ROOT drawing options to be used (excluding 'SAME'
    which is automatically applied for sub histograms on a pad).
    
    canvas_name is a prefix to use for the canvas name (a unique ID will 
    be added)
    
    set_y_zero toggles between setting the minimum y axis value to 0 or the 
    smallest value amongst the histograms
    
    sort_args is a list of arguments to be used in sorting the dictionary 
    keys. If separate sorts are required for sub-dictionaries then they 
    should be added to this list from position 3 otherwise the same
    sort will be used for both.
    """
    # use a function attribute to make all canvases unique
    increment_counter_attribute(get_canvas_with_hists, 'canvas_id')
    canvas_name = canvas_name + str(get_canvas_with_hists.canvas_id)
    
    # figure out how many pads the canvas needs to be divided into
    x,y = get_quantised_width_height(len(hists))
    canvas = make_canvas(canvas_name, n_x=x, n_y=y, resize=True)
    # make sure focus is on the correct canvas
    canvas.cd() 
    
    main_keys = get_sorted_dict_keys(hists, *sort_args[:3])
    for pad_id, pad_name in enumerate(main_keys, 1):
        canvas.cd(pad_id)        
        obj_to_draw = hists[pad_name]
        if not hasattr(obj_to_draw, 'keys'):
            # draw it an move on
            obj_to_draw.Draw(draw_opt)
        else:
            # collection of hists, to be drawn on the same pad
            sub_keys = get_sorted_dict_keys(obj_to_draw, *sort_args[3:])
            # figure out what the range should be
            axis_max = 1.1*get_max_amongst_hists(obj_to_draw)
            axis_min = 0.9*get_min_amongst_hists(obj_to_draw) if not set_y_zero else 0
            # t_draw_opt also is used to determine if this is the first hist
            t_draw_opt = draw_opt
            for colour_id, hist_name in enumerate(sub_keys, 1):
                hist = obj_to_draw[hist_name]
                # use t_draw_opt to determine if this is a virgin pad
                hist.SetMaximum(axis_max)
                hist.SetMinimum(axis_min)
                    
                hist.SetLineColor(colour_id)
                hist.Draw(t_draw_opt)
                t_draw_opt = "SAME"+draw_opt
                
    canvas.Update()
    return canvas


if __name__ == '__main__':
    test_make_hist()

