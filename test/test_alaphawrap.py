import pytest
import numpy as np
import ROOT
from TwoDAlphabet.alphawrap import *
from TwoDAlphabet.binning import Binning # Binning has been sufficiently tested

basedict = {
    "X": {
	"NAME": "xaxis",
	"TITLE": "xaxis",
	"MIN": 0,
	"MAX": 10,
	"NBINS": 10,
	"SIGSTART": 3,
	"SIGEND": 6
    },
    "Y": {
        "NAME": "yaxis",
        "TITLE": "yaxis",
        "MIN": 0,
        "MAX": 10,
        "NBINS": 10,
    }
}

'''
def filled_template(h):
    out = h.Clone('filled_test')
    gaus2d = ROOT.TF2('bigaus','bigaus',0,100,0,100)
    gaus2d.SetParameters(1, 50, 15, 50, 15) #amp,meanx,sigmax,meany,sigmay
    out.FillRandom('bigaus',10000)
    return out
'''
# we actually want a known distribution to test against 
def filled_template(h):
    out = h.Clone('filled_test')
    for x,y in itertools.product(range(1,h.GetNbinsX()+1),range(1,h.GetNbinsY()+1)):
        out.SetBinContent(x,y,1)
    return out

def filled_template_opposite(h):
    out = h.Clone('filled_test_opposite')
    for x,y in itertools.product(range(1,h.GetNbinsX()+1),range(1,h.GetNbinsY()+1)):
	out.SetBinContent(x,y,-1)
    return out

template = ROOT.TH2D('test','test',100,0,10,100,0,10)
filled = filled_template(template)
filled_opposite = filled_template_opposite(template)

binning = Binning('test',basedict,template)
print(binning.xbinByCat,binning.ybinList)

def test_BinnedDistribution():
    # NOTE: the BinnedDistribution object will *NOT* use the binning specified in the Y axis
    # In order for that to happen, one would have to use the OrganizedHists class
    bd = BinnedDistribution('test',filled,binning)
    print(len(bd.binVars))
