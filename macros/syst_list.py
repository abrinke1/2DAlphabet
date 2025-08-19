#! /usr/bin/env python
## Script to generate overlays of Nom/Up/Down distributions for systematics
import os
import sys
import ROOT as R
import numpy as np
import matplotlib.pyplot as plt

IN_DIR = '/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/raw_inputs/'

VERBOSE = False
DATE  = '2025_08_15'
#YEARS = ['2016preVFP','2016postVFP','2017','2018']
#MASSESA = ['12']+[str(mA*5) for mA in range(3,13)]
YEARS = ['Run2']
MASSESA = ['30']
MHREG   = 'pnet'  ## Higgs mass regression (mass, msoft, pnet)
MAREG   = '34a'   ## "a" boson mass regression (34a, 34d, 4a)
LUMI = {'2016preVFP':19.52, '2016postVFP':16.81, '2017':41.48, '2018':59.83}

## Super-categories and their component categories
SCATS = {}
SCATS['gg0lVHi'] = ['gg0lHi','VBFjjLoPtHi']
# SCATS['gg0lVLo'] = ['gg0lLo','VBFjjLoPtLo']
# SCATS['HadXHi']  = ['VBFjjHiPtHi','VjjHi']
# SCATS['HadXLo']  = ['VBFjjHiPtLo','VjjLo','tt0l0b']
# SCATS['LepHiT']  = ['tt0l1b','ZvvHi','Zll','WlvHi','ttbblv','ttll']
# SCATS['LepLo']   = ['ZvvLo','WlvLo','ttblv']
# SCATS['gg0lHi'] = ['gg0lHi']
CATS = {}
for scat in SCATS.keys():
    ## Set info for super-categories
    CATS[scat] = {}
    CATS[scat]['SCAT'] = scat
    ## Signal samples
    if scat.startswith('Lep'):
        CATS[scat]['SIGS'] = ['WH','ZH','ttH']
    else:
        CATS[scat]['SIGS'] = ['ggH','VBFH','WH','ZH','ttH']
    ## X4b WPs
    if scat.startswith('gg0l'):
        CATS[scat]['WP'] = 'WP40'
    elif scat.startswith('HadX'):
        CATS[scat]['WP'] = 'WP4060'
    else:
        CATS[scat]['WP'] = 'WP60'

    ## Set info for each sub-category
    for cat in SCATS[scat]:
        CATS[cat] = {}
        CATS[cat]['SCAT'] = scat
        ## Signal samples
        if cat[0:2] in ['Zv','Zl','Wl','tt']:
            CATS[cat]['SIGS'] = ['WH','ZH','ttH']
        else:
            CATS[cat]['SIGS'] = ['ggH','VBFH','WH','ZH','ttH']
        ## X4b WPs
        if cat.startswith('gg0l') or cat.startswith('VBFjj'):
            CATS[cat]['WP'] = 'WP40'
        else:
            CATS[cat]['WP'] = 'WP60'
    ## End loop: for cat in SCATS[scat]
## End loop: for scat in SCATS.keys()


def check_hist(hist):
    assert(hist.GetNbinsX() == 48)
    assert(hist.GetNbinsY() == 72)
    assert(hist.GetXaxis().GetBinLowEdge(23) == 110)
    assert(hist.GetXaxis().GetBinLowEdge(29) == 140)
    assert(hist.Integral() >= 0)
## End function: check_hist(hist)


def main():

    print('\n*** Running syst_list ***\n')
    hst = {}
    for ncat in CATS.keys():
        hst[ncat] = {}
        cat = CATS[ncat]
        for year in YEARS:
            print('\nStarting %s %s' % (ncat, year))
            hst[ncat][year] = {}
            for sig in cat['SIGS']:
                hst[ncat][year][sig] = {}
                for mA in MASSESA:
                    hst[ncat][year][sig][mA] = {}
                    hst[ncat][year][sig][mA]['2D'] = {}
                    hst[ncat][year][sig][mA]['mH'] = {}
                    hst[ncat][year][sig][mA]['mA'] = {}
                    ## Open input ROOT file
                    fn_sig = None
                    ncatwp = ncat+'/WP60' if ncat[0:3] in ['Zll','Wlv','ttb'] else ncat
                    fn_dir1 = IN_DIR+DATE+'/'+ncatwp+'/'+year+'/'
                    fn_sig1 = fn_dir1+ncat+'_'+sig+'toaato4b_mA_'+mA+'_'+year+'.root'
                    fn_dir2 = IN_DIR+DATE+'/2D_in_merged_'+cat['SCAT']+'/'+year+'/'
                    fn_sig2 = fn_dir2+cat['SCAT']+'_'+sig+'toaato4b_mA_'+mA+'_'+year+'.root'
                    fn_sig = fn_sig1 if os.path.exists(fn_sig1) else (fn_sig2 if os.path.exists(fn_sig2) else 'XXX')
                    try:
                        if VERBOSE: print('Opening '+fn_sig)
                        f_sig = R.TFile(fn_sig, 'open')
                    except:
                        print('\n*** ERROR! Problem with file:')
                        print(fn_sig)
                        print('Skipping. Files considered were:')
                        print(fn_sig1+' (exists = %s)' % os.path.exists(fn_sig1))
                        print(fn_sig2+' (exists = %s)' % os.path.exists(fn_sig2))
                        continue
                    ## Get input ROOT histograms
                    hn_sig = ncat+'_'+sig+'toaato4b_mA_'+mA+'_'+year+'_'+MHREG+'_'+MAREG+'_'+cat['WP']+'_Pass_'
                    try:
                        h_sig_nom = f_sig.Get(hn_sig+'Nom')
                        check_hist(h_sig_nom)
                    except:
                        print('\n*** ERROR! Problem with histogram in file:')
                        print(hn_sig)
                        print(fn_sig)
                        continue
                    ## Get list of systematics
                    all_hst = [hn.GetName() for hn in f_sig.GetListOfKeys() if hn.GetName().startswith(hn_sig)]
                    systs = [hn.replace(hn_sig,'')[:-4] for hn in all_hst if hn.endswith('Down')]
                    if VERBOSE or ncat in SCATS.keys():
                        print('\nSystematics in %s for %s, %s, %s:' % (ncat, year, sig, mA))
                        print(systs)

                    f_sig.Close()
                    del f_sig
                ## End loop: for mA in MASSESA
            ## End loop: for sig in cat['SIGS']
        ## End loop: for year in YEARS
    ## End loop: for ncat in CATS.keys()

    print('\n*** All done with syst_list! ***\n')
    
## End function: def main()

if __name__ == '__main__':
    main()
