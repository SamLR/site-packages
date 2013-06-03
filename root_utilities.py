#!/usr/bin/env python
# encoding: utf-8
"""
root_utilities.py

Created by Sam Cook on 2012-07-25.

Generally useful functions for dealing with ROOT objects
"""

from ROOT import gROOT, TFile, TTree, TBranch, TCanvas, TLegend, \
                 TH1D, TH2D, TH3D, TF1

from general_utilities import get_quantised_width_height, \
                                increment_counter_attribute
from ValueWithError import ValueWithError

from list_utilities import get_sorted_dict_keys

from sys import maxint

class ROOTException(Exception):
    pass


  

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


def get_tree_from_file(treename, filename):
  """
  Returns the requested tree from the file.
  
  To avoid loss of scope on the file it is attached as an 
  attribute of the tree (.file), along with the filename 
  (.filename)
  """
  file = TFile(filename,"READ")
  tree = file.Get(treename)
  tree.file = file
  tree.filename = filename
  return tree
  
if __name__ == '__main__':
    test_make_hist()

