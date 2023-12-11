import itertools
from TwoDAlphabet.binning import *
from ROOT import TH2F
import pytest
from copy import deepcopy
import numpy as np

basedict = {
    "HELP": "The binning of the x and y axes should be configured here",
    "X": {
        "NAME": "xaxis",
        "TITLE": "xaxis",
        "MIN": 0.0,
        "MAX": 1.0,
        "NBINS": 10,
        "SIGSTART": 0.3,
        "SIGEND": 0.7
    },
    "Y": {
        "NAME": "yaxis",
        "TITLE": "yaxis",
        "MIN": 0.0,
	"MAX": 1.0,
	"NBINS": 4
    }
}

def filled_template(h):
    out = h.Clone('filled_test')
    for x,y in itertools.product(range(1,h.GetNbinsX()+1),range(1,h.GetNbinsY()+1)):
        out.SetBinContent(x,y,1)
    return out

template = TH2F('test','test',20,0.0,1.0,20,0.0,1.0) # Let the basedict bins be a subset of the histo bins
filled = filled_template(template)

def test_BinningBase():
    b = Binning('test',basedict,template)
    assert(b.xbinList == [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    assert(b.xbinByCat == {"LOW":[0.0,0.1,0.2,0.3],"SIG":[0.3,0.4,0.5,0.6,0.7],"HIGH":[0.7,0.8,0.9,1.0]})
    assert(b.ybinList == [0.0, 0.25, 0.5, 0.75, 1.0])

def test_BinningSubsetX():
    test_dict = deepcopy(basedict)
    test_dict['X']['MIN'] = 0.0
    test_dict['X']['MAX'] = 1.0
    test_dict['X']['NBINS'] = 10
    b = Binning('test',test_dict,template)
    assert(b.xbinList == [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    assert(b.xbinByCat == {"LOW":[0.0,0.1,0.2,0.3],"SIG":[0.3,0.4,0.5,0.6,0.7],"HIGH":[0.7,0.8,0.9,1.0]})

def test_BinningSubsetY():
    test_dict = deepcopy(basedict)
    test_dict['Y']['MIN'] = 0.0
    test_dict['Y']['MAX'] = 1.0
    test_dict['Y']['NBINS'] = 4
    b = Binning('test',test_dict,template)
    assert(b.ybinList == [0.0, 0.25, 0.5, 0.75, 1.0])

def test_IsValidSubset():
    '''Checks whether or not the generated bin list is valid for different combinations.'''
    test_dict = deepcopy(basedict)
    test_dict['Y']['MIN'] = 0.0
    test_dict['Y']['MAX'] = 1.0
    bin_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for nbins in bin_numbers:
	test_dict['Y']['NBINS'] = nbins
	b = Binning('test',test_dict,template)
	assert(b.ybinList == [round(i,2) for i in np.linspace(0.0, 1.0, nbins, endpoint=False)]+[1.0])

def test_BinningVariableX():
    test_dict = deepcopy(basedict)
    test_dict['X'].pop('MIN')
    test_dict['X'].pop('MAX')
    test_dict['X'].pop('NBINS')
    test_dict['X']['BINS'] = [0.0, 0.11, 0.15, 0.3, 0.35, 0.5, 0.56, 0.61, 0.7, 0.8, 0.85, 0.9, 1.0]
    b = Binning('test',test_dict,template)
    assert(b.xbinList == [0.0, 0.11, 0.15, 0.3, 0.35, 0.5, 0.56, 0.61, 0.7, 0.8, 0.85, 0.9, 1.0])
    assert(b.xbinByCat == {"LOW":[0.0,0.11,0.15,0.3],"SIG":[0.3,0.35,0.5,0.56,0.61,0.7],"HIGH":[0.7,0.8,0.85,0.9,1.0]})

def test_BinningVariableY():
    test_dict = deepcopy(basedict)
    test_dict['Y'].pop('MIN')
    test_dict['Y'].pop('MAX')
    test_dict['Y'].pop('NBINS')
    test_dict['Y']['BINS'] = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,0.99,1.0]
    b = Binning('test',test_dict,template)
    assert(b.ybinList == [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.85,0.9,0.95,0.99,1.0])

def test_BinningBreakLowerX():
    test_dict = deepcopy(basedict)
    test_dict['X']['MIN'] = -2

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

def test_BinningBreakLowerY():
    test_dict = deepcopy(basedict)
    test_dict['Y']['MIN'] = -2

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

def test_BinningBreakUpperX():
    test_dict = deepcopy(basedict)
    test_dict['X']['MAX'] = 26

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

def test_BinningBreakUpperY():
    test_dict = deepcopy(basedict)
    test_dict['Y']['MAX'] = 22

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

def test_BinningOrderX():
    test_dict = deepcopy(basedict)
    del test_dict['X']['MIN']
    del test_dict['X']['MAX']
    del test_dict['X']['NBINS']
    test_dict['X']['BINS'] = [0.0, 0.1, 0.2, 0.3, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

def test_BinningOrderY():
    test_dict = deepcopy(basedict)
    del test_dict['Y']['MIN']
    del test_dict['Y']['MAX']
    del test_dict['Y']['NBINS']
    test_dict['Y']['BINS'] = [0.0, 0.1, 0.2, 0.3, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    with pytest.raises(ValueError):
        b = Binning('test',test_dict,template)

