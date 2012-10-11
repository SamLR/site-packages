#!/usr/bin/env python
# encoding: utf-8
"""
utilities.py

Created by Sam Cook on 2012-07-25.

Generally useful functions for dealing with ROOT objects
"""

from ROOT import gROOT, TFile, TTree, TBranch, TCanvas, TH1F, TLegend

from general_utilities import get_quantised_width_height

from sys import maxint

class ROOTException(Exception):
    pass

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
    


def make_hist(name, xmin, xmax, xtitle, ytitle, description=None):
    description = description if description != None else name
    res = TH1F(name, description, (xmax - xmin), xmin, xmax)
    res.GetXaxis().SetTitle(xtitle)
    res.GetYaxis().SetTitle(ytitle)
    return res


def rebin_nbins(hist, n_bins, new_name=''):
    """
    Rebins a histogram to have n_bins, if new_name is not provided then 
    the original is modified. 
    NOTE: if n_bins is not an exact factor of the existing number of bins 
    then n_bins will be created and the excess (at the upper bin) will be 
    added to the overflow bin
    """
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
    if bin_width == 0: 
        return hist
    else:
        return hist.Rebin(bin_width, new_name)


def make_canvas(name, n_x=0, n_y=0, maximised=False):
    name = str(name)
    canvas = TCanvas(name, name,1436,856) if maximised else TCanvas(name,name) 
    if n_x or n_y: canvas.Divide(n_x, n_y)
    return canvas


def get_dict_of_keys_and_tfile(filename, keyfunc=lambda x:x):
    """
    Opens the named TFile and creates a dictionary out of the 
    objects saved with in it. 
    
    The returned dictionary is formed of object:object_name pairs
    
    The pointer to the file is also returned to keep it in scope.
    
    Keyfunc is a function applied to the object's name to create 
    the dictionary key
    """
    # TODO Look at creating a recursive version of this
    # i.e. if the object has crawlable sub structure (trees, dirs etc)
    # write it into a dict format
    in_file = TFile(filename, "READ")
    res = {}
    for key in in_file.GetListOfKeys():
        # name looks like "Muon_momentum_with_Aluminium_0.5mm"
        obj = key.ReadObj()
        key = keyfunc(obj.GetName())
        res[key] = obj
    return res, in_tfile


def print_square_matrix(matrix):
    dimension = matrix.GetNcols()
    fmt_string = "% 5.2e " * dimension 
    for i in range (dimension):
        row = tuple([matrix[i][n] for n in range(dimension)])
        print fmt_string % row


def set_param_and_error(param_number, param, error, function):
    function.SetParameter(param_number, param)
    function.SetParError (param_number, error)


def get_param_and_error(param_number, function):
    return function.GetParameter(param_number), function.GetParError(param_number)


def set_bin_val_er_label(hist, bin, val, er, bin_name):
    hist.SetBinContent(bin, float(val))
    hist.SetBinError(bin, float(er))
    hist.GetXaxis().SetBinLabel(bin, str(bin_name))


def __get_x_amongst_hists(hists, initial_val, x_func, comp_func):
    """
    Helper function; apply x_func to all histograms in hists
    if comp_func(previous_val, returned_val) is true
    then returned_val set.
    """
    if hasattr(hists, 'keys'): hists = hists.values()
    res = initial_val
    for hist in hists:
        val = x_func(hist)
        if comp_func(res, val):
            res = val
    return res


def get_max_amongst_hists(hists):
    """
    Find the maximum value amongst hists
    """
    return __get_x_amongst_hists(hists, (-maxint - 1), 
                                lambda hist: hist.GetMaximum(),
                                lambda prev, this_val: prev < this_val)
        


def get_min_amongst_hists(hists):
    """
    Find the minimum value amongst hists
    """
    return __get_x_amongst_hists(hists, maxint,
                                lambda hist: hist.GetMinimum(),
                                lambda prev, this_val: prev > this_val)


def get_canvas_with_hists(hists, draw_opt='', canvas_name='c', set_y_min=False,
                        pad_preffix='', legend_preffix=''):
    """
    Draws given hists to a canvas. Assumes hists is either a dictionary
    of 
        <hist title>:<histogram> 
    pairs or a dictionary of 
        <hist title>:{<sub histogram title>:<sub histograms>} 
    pairs. 
    For either a single canvas will be divided into pads (1 per pair), 
    in the later case the sub-histograms will be all drawn to the same pad
    and the sub histogram title will be used in the appropriate legend.
    
    draw_opt are any ROOT drawing options to be used.
    canvas_name is a prefix to use for the canvas name (a unique ID will 
    be added)
    set_y_min toggles setting the minimum y value, useful for small ranges
    of values far from the origin.
    """
    # use a function attribute to make all canvases unique
    if not hasattr(get_canvas_with_hists, "canvas_id"):
        get_canvas_with_hists.canvas_id = 0
    else:
        get_canvas_with_hists.canvas_id += 1
    canvas_name = canvas_name + str(get_canvas_with_hists.canvas_id)
    # figure out how many pads the canvas needs to be divided into
    x,y = get_quantised_width_height(len(hists))
    canvas = make_canvas(canvas_name, n_x=x, n_y=y, maximised=True)
    canvas.save_legends = {}
    for pad_id, (pad_name, obj_to_draw) in enumerate(hists.items(), 1):
        pad = canvas.cd(pad_id)
        if not hasattr(obj_to_draw, 'keys'):
            # single hist draw it and move on
            obj_to_draw.SetTitle(pad_name)
            obj_to_draw.Draw(draw_opt)
        else:
            # collection of hists, to be drawn on the same pad
            axis_max = get_max_amongst_hists(obj_to_draw)
            if set_y_min: axis_min = get_min_amongst_hists(obj_to_draw)
            legend = TLegend(0.6, 0.9-0.04*len(obj_to_draw),0.8,0.9)
            legend.SetFillColor(0)
            first_hist = None
            for colour_id, (hist_name, hist) in enumerate(obj_to_draw.items(),1):
                if first_hist==None:
                    hist.SetMaximum(1.1*axis_max)
                    if set_y_min: hist.SetMinimum(0.9*axis_min)
                    hist.Draw(draw_opt)
                    first_hist=hist
                else:
                    hist.SetLineColor(colour_id)
                    hist.Draw(draw_opt+"SAME")
                legend.AddEntry(hist, legend_preffix + hist_name)
            first_hist.SetTitle(pad_preffix+str(pad_name)) 
            legend.Draw()
            # make sure that the legend objects stay in scope
            # mmmmm smells like impending memory leak!
            canvas.save_legends[pad_id] = legend
            pad.Update()
    return canvas


if __name__ == '__main__':
    pass

