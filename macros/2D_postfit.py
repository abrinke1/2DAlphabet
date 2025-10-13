#! /usr/bin/env python
## Script to generate overlays of Nom/Up/Down distributions for systematics
import os
import sys
import shutil
import ROOT as R
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

R.gROOT.SetBatch(True)  ## Don't draw histograms to screen
R.gStyle.SetOptStat(0)  ## Don't display stat boxes
R.gStyle.SetPalette(R.kTemperatureMap) ## Blue low --> white middle --> red high
## https://root.cern/doc/master/classTColor.html#C06

VERBOSE = False
DO_PLOTS = False
DATE = '2025_09_31'
NTOY = 30
#CATS = ['gg0lVHi','gg0lVLo']
#YEARS = ['2016','2017','2018']
#FITS = ['0x0C','1d1C','1x1C','2s2C','2x2C','3m3C']
#CATS = ['VBFjjHiPtHi','VjjHi400','VBFjjHiPtLo','VjjTLo','HadXHi','HadXLo']
#CATS = ['LepHiT','LepLo']
#YEARS = ['Run2']
#FITS = ['0x0C','1d1C','1x1C','2s2C']
CATS = ['gg0lVLo']
YEARS = ['2018']
FITS = ['2s2C']
DMC  = sys.argv[1] ## MC, Data
COLORS = [1,2,3,4,6,7,8,9,12,28,30,38,40,42,46,49]

IN_DIR  = '/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/output/%s/' % DATE
OUT_DIR = './plots/2D_postfit/'
# ## Some logic is buggy with rebinned pulls
# REBINS  = ['']
# for i in range(1,3):
#     for j in range(1,4):
#         REBINS.append('X%dY%d' % (i,j))
REBINS  = ['X1Y1']
YMIN = 0.5
YMAX = 2.5
PLOT_TOY = 3
NTOY_TOY = 400


## Chi2-like pull value based on beta-binomial test
## From https://gitlab.cern.ch/kkaspar/dqm-project/-/blob/master/python/beta_binomial.py?ref_type=heads#L241
def get_pull(iObsPass, iExpPass, iObsFail, iExpFail):
    ## Compute arbitrarily large number of events out of which the number in the bin is selected
    xExpPass = iObsFail*iExpPass/iExpFail  ## a-priori "expected" is observed in "fail" x expected pass/fail ratio
    nPass = 1000000000
    nFail = int(round(nPass*iObsFail/xExpPass))
    probObs = stats.betabinom.pmf(iObsPass, nPass, iObsFail + 1, nFail - iObsFail + 1)
    probExpLo = stats.betabinom.pmf(int(round(np.floor(xExpPass))), nPass, iObsFail + 1, nFail - iObsFail + 1)
    probExpHi = stats.betabinom.pmf( int(round(np.ceil(xExpPass))), nPass, iObsFail + 1, nFail - iObsFail + 1)
    ## chi2.isf function fails for probRel < 10^-323, so cap at 10^-300 (37 sigma)
    probRel = max(probObs / max(probExpLo, probExpHi), pow(10, -300))
    if probRel < 0.0 or probRel > 1.0:
        print([iObsPass, int(round(np.floor(xExpPass))), int(round(np.ceil(xExpPass)))])
        print([probObs, probExpLo, probExpHi, probRel])
        sys.exit()
    pull = np.sqrt(-2*np.log(probRel))
    pull *= (1 if iObsPass > xExpPass else -1)
    return pull
## End function: get_pull(iObsPass, xExpPass, iObsFail, iExpFail)
    

def get_postfit_plots_pulls(cat, year, iToy, fit):

    wp = 'WP40' if cat[:4] in ['gg0l','VBFj'] else ('WP4060' if cat[:4] == 'HadX' else 'WP60')
    samp = '%s_Htoaato4b_pnet_34a_%s_%s_%s_toy%d' % (cat, wp, fit, year, iToy)
    in_fname = IN_DIR+'%stoys/fits_%s/mA_all_area/postfitshapes_b.root' % (DMC, samp)
    GoF_name = IN_DIR.replace('output','ToyStudies')
    GoF_name += ('%s/%s/higgsCombine.testGoodnessOfFit.%s.mA_12.%s.%stoy%d.GoodnessOfFit.mH120.root' % \
                 (cat, year, cat, fit, DMC, iToy))

    print('*** Running %s %s %s %d %s ***' % (DMC, cat, year, iToy, fit))
    hst = {}
    ## Open input ROOT file
    if os.path.exists(in_fname):
        in_f = R.TFile(in_fname, 'open')
    else:
        if VERBOSE: print('Missing %s: skipping.' % in_fname)
        return None, None
    GoF_f = None
    if os.path.exists(GoF_name):
        GoF_f = R.TFile(GoF_name, 'open')
    else:
        if VERBOSE: print('Missing %s: skipping.' % GoF_name)

    ## Get input ROOT histograms
    xr,yr = {},{}
    for PF in ['Pass','Fail']:
        for mH in ['LOW','SIG','HIGH']:
            if not mH in xr.keys():
                xr[mH] = []
            if not mH in yr.keys():
                yr[mH] = []
            #for prps in ['prefit','postfit']:
            for prps in ['postfit']:
                in_d = '%s_%s_%s' % (PF, mH, prps)
                hst[in_d] = {}
                hst[in_d]['bkg']  = in_f.Get(in_d+'/TotalBkg')
                hst[in_d]['sig']  = in_f.Get(in_d+'/TotalSig')
                hst[in_d]['data'] = in_f.Get(in_d+'/data_obs')
                for key in hst[in_d].keys():
                    hst[in_d][key].SetDirectory(0)
                xr[mH] = [hst[in_d]['bkg'].GetXaxis().GetBinLowEdge(1),
                          hst[in_d]['bkg'].GetXaxis().GetBinUpEdge( hst[in_d]['bkg'].GetNbinsX() )]
                yr[mH] = [hst[in_d]['bkg'].GetYaxis().GetBinLowEdge(1),
                          hst[in_d]['bkg'].GetYaxis().GetBinUpEdge( hst[in_d]['bkg'].GetNbinsY() )]
            ## End loop: for prps in ['prefit','postfit']
        ## End loop: for mH in ['LOW','SIG','HIGH']
    ## End loop: for PF in ['Pass','Fail']


    ## Generate 'ALL' histograms combining LOW, SIG, and HIGH
    ## Use finest available binning, but fill every bin
    ## For visualization ONLY, e.g. does not have same integral as LOW+SIG+HIGH
    for PF in ['Pass','Fail']:
        #for prps in ['prefit','postfit']:
        for prps in ['postfit']:
            out_d = '%s_ALL_%s' % (PF, prps)
            hst[out_d] = {}
            for key in ['bkg','sig','data']:
                hst[out_d][key] = R.TH2D(out_d+'_'+key, out_d+'_'+key,
                                         int(round((xr['HIGH'][1]-xr['LOW'][0]) / 10)), xr['LOW'][0], xr['HIGH'][1],
                                         int(round(yr['HIGH'][1]-yr['LOW'][0])), yr['LOW'][0], yr['HIGH'][1])
                hst[out_d][key].SetDirectory(0)
                for iX in range(1, hst[out_d][key].GetNbinsX()+1):
                    cX = hst[out_d][key].GetXaxis().GetBinCenter(iX)
                    mH = 'LOW' if cX < xr['LOW'][1] else ('HIGH' if cX > xr['HIGH'][0] else 'SIG')
                    for iY in range(1, hst[out_d][key].GetNbinsY()+1):
                        in_d = '%s_%s_%s' % (PF, mH, prps)
                        jX = hst[in_d][key].GetXaxis().FindBin( hst[out_d][key].GetXaxis().GetBinCenter(iX) )
                        jY = hst[in_d][key].GetYaxis().FindBin( hst[out_d][key].GetYaxis().GetBinCenter(iY) )
                        hst[out_d][key].SetBinContent(iX, iY, hst[in_d][key].GetBinContent(jX,jY))
                        hst[out_d][key].SetBinError(iX, iY, hst[in_d][key].GetBinError(jX,jY))
                    ## End loop: for iY in range(1, hst[out_d][key].GetNbinsY()+1)
                ## End loop: for iX in range(1, hst[out_d][key].GetNbinsX()+1)

            ## End loop: for key in ['bkg','sig','data']
        ## End loop: for mH in ['LOW','SIG','HIGH']
    ## End loop: for PF in ['Pass','Fail']


    metr = {}
    if iToy == PLOT_TOY:
        toy_pullSq = {}
        binSqAll = 0
        for mH in ['LOW','SIG','HIGH','ALL']:
            toy_pullSq[mH] = [0 for i in range(NTOY_TOY)]
    ## Compute pulls and fill pull and ratio plots
    for mH in ['ALL','LOW','SIG','HIGH']:
        metr[mH] = {}
        #for prps in ['prefit','postfit']:
        for prps in ['postfit']:
            out_d = 'Ratio_%s_%s' % (mH, prps)
            hst[out_d] = {}
            for key in ['bkg','data']:
                hst[out_d][key] = hst['Pass_%s_%s' % (mH, prps)][key].Clone(out_d+'_'+key)
                hst[out_d][key].SetDirectory(0)
                hst[out_d][key].SetTitle(out_d+'_'+key)
                hst[out_d][key].Divide(hst['Fail_%s_%s' % (mH, prps)][key])
            ## End loop: for key in ['bkg','data']
            for PF in ['Pass','Fail']:
                out_d = '%s_%s_%s' % (PF, mH, prps)
                hst[out_d]['ratio'] = hst[out_d]['data'].Clone(out_d+'_ratio')
                hst[out_d]['ratio'].SetDirectory(0)
                hst[out_d]['ratio'].SetTitle(out_d+'_ratio')
                hst[out_d]['ratio'].Divide(hst[out_d]['bkg'])

                if mH != 'ALL' and prps != 'prefit' and VERBOSE:
                    print('Getting pulls for %s %s %s' % (mH, prps, PF))

                for REB in REBINS:
                    if prps == 'postfit' and PF == 'Pass':
                        metr[mH][REB] = {}
                    REBs = '_reb'+REB if REB != 'X1Y1' else ''
                    hst[out_d]['pull'+REBs] = hst[out_d]['data'].Clone(out_d+'_pull'+REBs)
                    hst[out_d]['pull'+REBs].SetDirectory(0)
                    hst[out_d]['pull'+REBs].SetTitle(out_d+'_pull'+REBs)
                    hst[out_d]['pullSq'+REBs] = hst[out_d]['data'].Clone(out_d+'_pullSq'+REBs)
                    hst[out_d]['pullSq'+REBs].SetDirectory(0)
                    hst[out_d]['pullSq'+REBs].SetTitle(out_d+'_pullSq'+REBs)
                    if PF != 'Pass' or prps != 'postfit' or mH == 'ALL':
                        continue

                    out_df = out_d.replace('Pass_','Fail_')
                    ihd  = hst[out_d]['data'].Clone('ihd')
                    ihdf = hst[out_df]['data'].Clone('ihdf')
                    ihb  = hst[out_d]['bkg'].Clone('ihb')
                    ihbf = hst[out_df]['bkg'].Clone('ihbf')
                    rX = int(REB[1])
                    rY = int(REB[3])
                    ihd.Rebin2D(rX,rY)
                    ihdf.Rebin2D(rX,rY)
                    ihb.Rebin2D(rX,rY)
                    ihbf.Rebin2D(rX,rY)
                    binSq,useSq,wgtSq,Nbin,Nuse,Nwgt = 0,0,0,0,0,0
                    for iX in range(1, ihd.GetNbinsX()+1):
                        for iY in range(1, ihd.GetNbinsY()+1):
                            ## Compute observed pulls per bin vs. expectation
                            iObsPass = int(round(ihd.GetBinContent(iX, iY)))
                            iExpPass = float(ihb.GetBinContent(iX, iY))
                            eExpPass = float(ihb.GetBinError(iX, iY))
                            #pull = (iObsPass - iExpPass) / np.sqrt(max(1, iObsPass+1 + pow(eExpPass,2)))
                            if PF == 'Pass':
                                iObsFail = int(round(ihdf.GetBinContent(iX, iY)))
                                iExpFail = float(ihbf.GetBinContent(iX, iY))
                            elif PF == 'Fail':
                                iObsFail = int(round(1000000*iExpPass))
                                iExpFail = float(1000000*iExpPass)
                            pull = get_pull(iObsPass, iExpPass, iObsFail, iExpFail)
                            Nbin += 1
                            binSq += pow(pull, 2)
                            Nwgt += iExpPass
                            wgtSq += pow(pull, 2)*iExpPass
                            if (iObsPass > 0 or iExpPass > 1):
                                Nuse += 1
                                useSq += pow(pull, 2)
                            hst[out_d]['pull'+REBs].SetBinContent(iX, iY, pull)
                            hst[out_d]['pullSq'+REBs].SetBinContent(iX, iY, pull*pull*(-1 if pull < 0 else 1))

                            ## Generate toy data from expectation for each bin
                            if iToy == PLOT_TOY and prps == 'postfit' and PF == 'Pass' and mH != 'ALL':
                                for jToy in range(NTOY_TOY):
                                    iObsPassToy = int(round(np.random.poisson(iObsFail*iExpPass/iExpFail)))
                                    #iObsFailToy = int(round(np.random.poisson(iExpFail)))
                                    #print('Threw toy %d/%d from %.3f/%.3f' % (iObsPassToy, iObsFail, iExpPass, iExpFail))
                                    #toy_pass[jToy].SetBinContent(iX, iY, iObsPassToy)
                                    pull_jToy = get_pull(iObsPassToy, iExpPass, iObsFail, iExpFail)
                                    toy_pullSq[mH][jToy] += pow(pull_jToy, 2)
                                    toy_pullSq['ALL'][jToy] += pow(pull_jToy, 2)
                            
                            ## Fill "ALL" histogram with contents from LOW, SIG, and HIGH
                            out_da = out_d.replace(mH, 'ALL')
                            for jX in range(1, hst[out_da][key].GetNbinsX()+1):
                                if hst[out_da][key].GetXaxis().GetBinCenter(jX) >= ihd.GetXaxis().GetBinLowEdge(iX) and \
                                   hst[out_da][key].GetXaxis().GetBinCenter(jX) <= ihd.GetXaxis().GetBinUpEdge(iX):
                                    for jY in range(1, hst[out_da][key].GetNbinsY()+1):
                                        if hst[out_da][key].GetYaxis().GetBinCenter(jY) >= ihd.GetYaxis().GetBinLowEdge(iY) and \
                                           hst[out_da][key].GetYaxis().GetBinCenter(jY) <= ihd.GetYaxis().GetBinUpEdge(iY):
                                            hst[out_da]['pull'+REBs].SetBinContent(jX, jY, pull)
                                            hst[out_da]['pullSq'+REBs].SetBinContent(jX, jY, pull*pull*(-1 if pull < 0 else 1))
                        ## End loop: for iY in range(1, ihd.GetNbinsY()+1)
                    ## End loop: for iX in range(1, ihd.GetNbinsX()+1)                     
                    if prps == 'postfit' and PF == 'Pass' and mH != 'ALL':
                        metr[mH][REB]['binSq'] = binSq
                        metr[mH][REB]['useSq'] = useSq
                        metr[mH][REB]['wgtSq'] = wgtSq
                        metr[mH][REB]['Nbin'] = Nbin
                        metr[mH][REB]['Nuse'] = Nuse
                        metr[mH][REB]['Nwgt'] = Nwgt
                        #if VERBOSE:
                        if iToy == PLOT_TOY:
                            print('%s %s %s %d %s %s rebin%s Chi2/NDoF = %.1f/%d or %.1f/%d or %.1f/%d (%.3f or %.3f or %.3f)' % \
                                  (DMC, cat, year, iToy, fit, mH, REB, binSq, Nbin, useSq, \
                                   Nuse, wgtSq, Nwgt, binSq/Nbin, useSq/Nuse, wgtSq/Nwgt))
                            tpl = sorted(toy_pullSq[mH])
                            binSqAll += binSq
                            print('From %d toys, mean %s Chi2 = %.2f, median %.2f, 68%% range [%.2f, %.2f], 95%% range [%.2f, %.2f]' % \
                                  (len(tpl), mH, sum(tpl) / len(tpl), tpl[int(len(tpl)/2)], \
                                   tpl[int(0.16*len(tpl))], tpl[int(0.84*len(tpl))], tpl[int(0.025*len(tpl))], tpl[int(0.975*len(tpl))]))
                            print('Observed Chi2 = %.1f p-value is %.1f%%' % (binSq, 100*len([x for x in tpl if x > binSq])/len(tpl)))
                    if iToy == PLOT_TOY and prps == 'postfit' and PF == 'Pass' and mH == 'HIGH':
                        tpl = sorted([toy_pullSq['LOW'][ii]+toy_pullSq['SIG'][ii]+toy_pullSq['HIGH'][ii] for ii in range(NTOY_TOY)])
                        print('From %d toys, mean ALL Chi2 = %.2f, median %.2f, 68%% range [%.2f, %.2f], 95%% range [%.2f, %.2f]' % \
                              (len(tpl), sum(tpl) / len(tpl), tpl[int(len(tpl)/2)], \
                               tpl[int(0.16*len(tpl))], tpl[int(0.84*len(tpl))], tpl[int(0.025*len(tpl))], tpl[int(0.975*len(tpl))]))
                        print('Observed Chi2 = %.1f p-value is %.1f%%' % (binSqAll, 100*len([x for x in tpl if x > binSqAll])/len(tpl)))

                    del ihd
                    del ihdf
                    del ihb
                    del ihbf
                ## End loop: for REB in REBINS
            ## End loop: for PF in ['Pass','Fail']
        ## End loop: for prps in ['prefit','postfit']
    ## End loop: for mH in ['LOW','SIG','HIGH','ALL']

    ## Add up metrics for 'ALL' distribution
    for REB in REBINS:
        for key in metr['LOW'][REB].keys():
            metr['ALL'][REB][key] = metr['LOW'][REB][key]+metr['SIG'][REB][key]+metr['HIGH'][REB][key]
    if not GoF_f == None:
        GoF_tree = GoF_f.Get('limit')
        has_GoF = False
        try:
            for entry in GoF_tree:
                assert (not has_GoF), '\nWEIRD ERROR! two observed values in file %s' % GoF_name
                assert (entry.iToy == 0), '\nWEIRD ERROR! iToy = %d in file %s' % (entry.iToy, GoF_name)
                has_GoF = True
                metr['ALL']['X1Y1']['GoF'] = entry.limit
        except:
            print('\nBuggy limit tree in %s, skipping\n' % GoF_name)

    return (hst, metr)
## End function: get_postfit_plots_pulls(cat, year, iToy, fit)


## Main executable function
def main():

    print('\n*** Running 2D_postfit: ***\n')

    hst = {}
    metr = {}
    trnd = {}
    can = {}
    for cat in CATS:
        hst[cat] = {}
        metr[cat] = {}
        trnd[cat] = {}
        can[cat] = {}
        for yr in YEARS:
            if cat[:4] in ['gg0l'] and yr[:3] != '201': continue
            if not cat[:4] in ['gg0l'] and yr != 'Run2': continue
            hst[cat][yr] = {}
            metr[cat][yr] = {}
            trnd[cat][yr] = {}
            can[cat][yr] = {}
            for iToy in range(NTOY):
                sTy = str(iToy)
                hst[cat][yr][sTy] = {}
                metr[cat][yr][sTy] = {}
                trnd[cat][yr][sTy] = {}
                for mH in ['LOW','SIG','HIGH','ALL']:
                    trnd[cat][yr][sTy][mH] = {}
                    if iToy == 0:
                        can[cat][yr][mH] = {}
                    for mtr in ['bin','use','wgt','GoF','Dbin','Duse','Dwgt','DGoF','Dratio']:
                        if 'GoF' in mtr and mH != 'ALL': continue
                        xs = np.array([0.5+i for i in range(len(FITS))])
                        ys = np.array([-0.2 for i in range(len(FITS))])
                        trnd[cat][yr][sTy][mH][mtr] = R.TGraph(len(xs), xs, ys)
                        trnd[cat][yr][sTy][mH][mtr].SetTitle('%s %s %s mH(%s) chi2 (%s)' % (cat, yr, DMC, mH, mtr)) 
                        trnd[cat][yr][sTy][mH][mtr].SetMarkerColor(COLORS[iToy % 15])
                        trnd[cat][yr][sTy][mH][mtr].SetMarkerStyle(8)
                        trnd[cat][yr][sTy][mH][mtr].SetMarkerSize(1)
                        if iToy == 0:
                            can[cat][yr][mH][mtr] = R.TCanvas('can_%s_%s_%s_%s_%s%s' % (cat, yr, DMC, mH, mtr, '' if 'GoF' in mtr else 'Sq'))
                for iFit in range(len(FITS)):
                    fit = FITS[iFit]
                    ohst, ometr = get_postfit_plots_pulls(cat, yr, iToy, fit)
                    if ohst == None or ometr == None: continue
                    hst[cat][yr][sTy][fit] = ohst
                    metr[cat][yr][sTy][fit] = ometr
                    for mH in ['LOW','SIG','HIGH','ALL']:
                        for mtr in ['bin','use','wgt','GoF',]:
                            if mtr == 'GoF' and mH != 'ALL': continue
                            if mtr == 'GoF' and not 'GoF' in ometr[mH]['X1Y1'].keys(): continue
                            sumSq = ometr[mH]['X1Y1'][mtr+'Sq' if mtr!='GoF' else mtr]
                            Nsum  = ometr[mH]['X1Y1']['N'+mtr if mtr!='GoF' else 'Nbin']
                            chiSq = max(YMIN+0.02, min(YMAX-0.02, sumSq/Nsum))
                            trnd[cat][yr][sTy][mH][mtr].SetPoint(iFit, iFit+0.5, chiSq)
                            if iFit > 0 and FITS[iFit-1] in metr[cat][yr][sTy].keys():
                                if mtr == 'GoF' and not 'GoF' in metr[cat][yr][sTy][FITS[iFit-1]][mH]['X1Y1'].keys(): continue
                                DsumSq = metr[cat][yr][sTy][FITS[iFit-1]][mH]['X1Y1'][mtr+'Sq' if mtr!='GoF' else mtr]
                                NDsum  = metr[cat][yr][sTy][FITS[iFit-1]][mH]['X1Y1']['N'+mtr if mtr!='GoF' else 'Nbin']
                                DchiSq = max(-0.09, min(0.39, DsumSq/NDsum - sumSq/Nsum))
                                trnd[cat][yr][sTy][mH]['D'+mtr].SetPoint(iFit, iFit+0.5, DchiSq)
                            #if True: #VERBOSE:
                            #    print('Setting %s %s %s %s %s point %d at (%.1f, %.3f)' % (cat, yr, sTy, mH, mtr, iFit, iFit+0.5, sumSq/Nsum))
                        ## End loop: for mtr in ['bin','use','wgt','GoF']
                        if iFit > 0 and FITS[iFit-1] in hst[cat][yr][sTy].keys() and \
                           not ohst['Ratio_%s_postfit' % mH]['bkg'] == None and \
                           not hst[cat][yr][sTy][FITS[iFit-1]]['Ratio_%s_postfit' % mH]['bkg'] == None:
                            htmpA = hst[cat][yr][sTy][FITS[iFit-1]]['Ratio_%s_postfit' % mH]['bkg'].Clone('htmpA')
                            htmpB = ohst['Ratio_%s_postfit' % mH]['bkg'].Clone('htmpB')
                            nBins = htmpA.GetNbinsX()*htmpA.GetNbinsY()
                            htmpA.Scale(nBins / htmpA.Integral())
                            htmpB.Scale(nBins / htmpB.Integral())
                            htmpB.Add(htmpA,-1)
                            htmpB.Multiply(htmpB)
                            trnd[cat][yr][sTy][mH]['Dratio'].SetPoint(iFit, iFit+0.5, min(0.099, htmpB.Integral() / nBins))
                    ## End loop: for mH in ['LOW','SIG','HIGH','ALL']

                    ## Draw histograms for individual outputs
                    if iToy == PLOT_TOY:
                        iSamp = '%s_%s_%s_toy%d' % (cat, fit, yr, iToy)
                        if os.path.exists(OUT_DIR+'pdf/%s_%s_%s/' % (DATE, iSamp, DMC)):
                            shutil.rmtree(OUT_DIR+'pdf/%s_%s_%s/' % (DATE, iSamp, DMC))
                        if not os.path.exists(OUT_DIR+'pdf/%s_%s_%s/' % (DATE, iSamp, DMC)):
                            os.makedirs(OUT_DIR+'pdf/%s_%s_%s/' % (DATE, iSamp, DMC))
                    for hd in ohst.keys():
                        if iToy != PLOT_TOY: break
                        for hk in ohst[hd].keys():
                            if 'prefit' in ohst[hd][hk].GetName(): continue
                            if '_ALL_' in ohst[hd][hk].GetName() or '_pull' in ohst[hd][hk].GetName():
                                if 'Fail' in ohst[hd][hk].GetName() and '_reb' in ohst[hd][hk].GetName():
                                    continue
                            hcan = R.TCanvas()
                            hcan.cd()
                            zMax = ohst[hd][hk].GetMaximum()
                            zMin = ohst[hd][hk].GetMinimum()
                            if '_pullSq' in ohst[hd][hk].GetName():
                                ohst[hd][hk].GetZaxis().SetRangeUser(-7.5,7.5)
                            elif '_pull' in ohst[hd][hk].GetName():
                                ohst[hd][hk].GetZaxis().SetRangeUser(-3.0,3.0)
                            if '_ratio' in ohst[hd][hk].GetName():
                                ohst[hd][hk].GetZaxis().SetRangeUser(0,2.0)
                            if 'Ratio_' in ohst[hd][hk].GetName():
                                dZ = max(zMax-zMin, 0.05)
                                ohst[hd][hk].GetZaxis().SetRangeUser(zMin-0.1*dZ, zMax+0.1*dZ)
                            ohst[hd][hk].Draw('colz')
                            hcan.SaveAs(OUT_DIR+'pdf/%s_%s_%s/%s_%s.pdf' % (DATE, iSamp, DMC, hd, hk))
                            if hd[:4] in  ['Pass','Fail'] and hk in ['bkg','data']:
                                ohst[hd][hk].GetZaxis().SetRangeUser(max(0.1, zMin/2), zMax*2)
                                #ohst[hd][hk].SetLogZ()
                                ohst[hd][hk].Draw('colz')
                                hcan.SetLogz()
                                hcan.SaveAs(OUT_DIR+'pdf/%s_%s_%s/%s_%s_logZ.pdf' % (DATE, iSamp, DMC, hd, hk))
                            del hcan
                        ## End loop: for hd in ohst.keys()
                    ## End loop: for hk in ohst[hd].keys()

                ## End loop: for fit in FITS

                ## Draw graphs from multiple toys onto the same canvas
                for mH in ['LOW','SIG','HIGH','ALL']:
                    for mtr in ['bin','use','wgt','GoF','Dbin','Duse','Dwgt','DGoF','Dratio']:
                        if 'GoF' in mtr and mH != 'ALL': continue
                        can[cat][yr][mH][mtr].cd()
                        dopt = ('SAME P' if iToy > 0 else 'AP')
                        mmY = [0,0.1] if mtr=='Dratio' else ([-0.1,0.4] if mtr[0]=='D' else [YMIN,YMAX])
                        trnd[cat][yr][sTy][mH][mtr].GetYaxis().SetRangeUser(mmY[0], mmY[1])
                        for ii in range(len(FITS)):
                            iBin = trnd[cat][yr][sTy][mH][mtr].GetXaxis().FindBin(ii+0.5)
                            trnd[cat][yr][sTy][mH][mtr].GetXaxis().SetBinLabel(iBin, FITS[ii])
                        trnd[cat][yr][sTy][mH][mtr].Draw(dopt)
                        #print('In canvas %s %s %s %s, adding toy %s with (%.1f, %.4f)' % (cat, yr, mH, mtr, sTy,
                        #                                                                  trnd[cat][yr][sTy][mH][mtr].GetPointX(1),
                        #                                                                  trnd[cat][yr][sTy][mH][mtr].GetPointY(1)))
            ## End loop: for iToy in range(NTOY)
            for mH in ['LOW','SIG','HIGH','ALL']:
                for mtr in ['bin','use','wgt','GoF','Dbin','Duse','Dwgt','DGoF','Dratio']:
                    if 'GoF' in mtr and mH != 'ALL': continue
                    can[cat][yr][mH][mtr].SaveAs(OUT_DIR+'pdf/%s.pdf' % can[cat][yr][mH][mtr].GetName())


        ## End loop: for yr in YEARS
    ## End loop: for cat in CATS




#     out_fname = OUT_DIR+'2D_postfit_%s_%s_%s.root' % (DATE, DMC, samp)


# if DO_PLOTS:
#     if os.path.exists(OUT_DIR+'pdf/%s_%s/' % (DATE, SAMP)):
#         shutil.rmtree(OUT_DIR+'pdf/%s_%s/' % (DATE, SAMP))
#     if not os.path.exists(OUT_DIR+'pdf/%s_%s/' % (DATE, SAMP)):
#         os.makedirs(OUT_DIR+'pdf/%s_%s/' % (DATE, SAMP))


#     out_f = R.TFile(OUT_FILE, 'recreate')
#     out_f.cd()
#     for hd in hst.keys():
#         for hk in hst[hd].keys():
#             hst[hd][hk].Write()
#             if 'prefit' in hst[hd][hk].GetName():
#                 continue
#             if '_ALL_' in hst[hd][hk].GetName() or '_pull' in hst[hd][hk].GetName():
#                 if 'Fail' in hst[hd][hk].GetName() and '_reb' in hst[hd][hk].GetName():
#                     continue
#                 can = R.TCanvas()
#                 can.cd()
#                 if '_pullSq' in hst[hd][hk].GetName():
#                     hst[hd][hk].GetZaxis().SetRangeUser(-6.25,6.25)
#                 elif '_pull' in hst[hd][hk].GetName():
#                     hst[hd][hk].GetZaxis().SetRangeUser(-3.0,3.0)
#                 if '_ratio' in hst[hd][hk].GetName():
#                     hst[hd][hk].GetZaxis().SetRangeUser(0,2.0)
#                 if 'Ratio_' in hst[hd][hk].GetName():
#                     zMax = hst[hd][hk].GetMaximum()
#                     zMin = hst[hd][hk].GetMinimum()
#                     dZ = max(zMax-zMin, 0.05)
#                     hst[hd][hk].GetZaxis().SetRangeUser(zMin-0.1*dZ, zMax+0.1*dZ)
#                 hst[hd][hk].Draw('colz')
#                 can.SaveAs(OUT_DIR+'pdf/%s_%s/%s_%s.pdf' % (DATE, SAMP, hd, hk))
#                 del can
#     out_f.Write()
#     del out_f

#     print('\nWrote outputs to:')
#     print(OUT_FILE)
#     print(OUT_DIR+'pdf/%s_%s/' % (DATE, SAMP))

    print('\n*** All done with 2D_postfit! ***\n')
    
## End function: def main()

if __name__ == '__main__':
    main()
