#! /usr/bin/env python
## Modified from https://github.com/bouchamaouihichem/2DAlphabet/blob/dev25_0501/merge_files_mctoy.py

## Script to estimate S/B ratio for various categories
## Updated to merge sub-categories into 2DAlphabet fit categories
import os
import sys
import shutil
import math
import ROOT as R
from array import array

R.gROOT.SetBatch(True)  ## Don't display histograms or canvases when drawn
R.gStyle.SetOptStat(0)  ## Don't display stat boxes

## User configuration
VERBOSE = False
PRINTONLY = False
HADSIGS  = ['ggH', 'VBFH', 'WH', 'ZH', 'ttH']
LEPSIGS  = ['WH', 'ZH', 'ttH']
MASSESA  = ['12']+[str(mA*5) for mA in range(3,13)]
#MHREGS   = ['mass', 'msoft','pnet']
#MAREGS   = ['34a', '34d', '4a']
MHREGS   = ['pnet']
MAREGS   = ['34a']
DATE     = '2025_07_25'
LUMIS    = {'2016preVFP': 19.52, '2016postVFP': 16.81, '2017': 41.48, '2018': 59.83}
eos_from_config = [eos for eos in (open('config/user.config','r')).readlines() if eos.startswith('EOS_DIR=')]
EOS_DIR = eos_from_config[0].replace('EOS_DIR=','').replace('\n','')

ONE_SAMP = ''  ## Run over a single sample matching a string, e.g. 'VBFHtoaato4b_mA_55'
CATS_IN = {}
CAT_OUT = sys.argv[1]  ## gg0lIncl, LepHi, LepLo, etc.
YEAR    = sys.argv[2]  ## 2016preVFP, 2016postVFP, 2017, 2018
CAT_INS = [CAT_OUT]
IN_DIR = EOS_DIR+'/raw_inputs/%s/' % DATE
if not os.path.exists('logs'):
    os.system('mkdir logs')


IS_HAD,IS_LEP = False,False
for pref in ['Had','gg0l','VBFjj','Vjj','VVBFjj','tt0l']:
    if CAT_OUT.startswith(pref):
        IS_HAD = True
for pref in ['Lep','Zll','Wlv','ttb','Zvv']:
    if CAT_OUT.startswith(pref):
        IS_LEP = True
assert (IS_HAD or IS_LEP), 'CAT_OUT %s not valid!!! Quitting.' % CAT_OUT

print('\nRunning merge_files_mctoy.py for %s' % CAT_OUT)
if IS_HAD:
    if CAT_OUT.endswith('Incl') and not CAT_OUT == 'tt0lIncl':
        CAT_INS = [CAT_OUT.replace('Incl','')+sub for sub in ['Lo','Hi']]
    if CAT_OUT == 'gg0lV':
        CAT_INS = ['gg0lLo','gg0lHi','VBFjjLo']
    if CAT_OUT == 'gg0lVLo':
        CAT_INS = ['gg0lLo','VBFjjLo']
    if CAT_OUT == 'VVBFjj':
        CAT_INS = ['VBFjjHi','VjjHi']
    if CAT_OUT == 'HadXLo':
        CAT_INS = ['VjjLo','tt0l0b']
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = [sig+'toaato4b' for sig in HADSIGS]
        CATS_IN[cat]['bkgs'] = ['QCD_BGen','QCD_bEnr','QCD_Incl','Wqq','Zqq','TT0l','TT1l','MC']  ## Put 'MC' at the end!!!
        CATS_IN[cat]['dir'] = IN_DIR+cat

elif IS_LEP:
    if CAT_OUT.startswith('Lep'):
        CAT_INS = []
        for pref in ['LepLo','LepIncl']:
            if CAT_OUT.startswith(pref):
                CAT_INS = CAT_INS+['ZvvLo','WlvLo','ttblv']
                break
        for pref in ['LepHi','LepIncl']:
            if CAT_OUT.startswith(pref):
                CAT_INS = CAT_INS+['ZvvHi','Zll','WlvHi','ttbblv','ttbll']
                if CAT_OUT == 'LepHiT':
                    CAT_INS = CAT_INS+['tt0l1b']
                break
        ## Check modifications to lepontic categorization
        if CAT_OUT == 'LepLoA': CAT_INS.remove('WlvLo')
        if CAT_OUT == 'LepHiA': CAT_INS.append('WlvLo')
        if CAT_OUT == 'LepLoB': CAT_INS.remove('ttblv')
        if CAT_OUT == 'LepHiB': CAT_INS.append('ttblv')
        if CAT_OUT == 'LepLoC': CAT_INS.append('WlvHi')
        if CAT_OUT == 'LepHiC': CAT_INS.remove('WlvHi')
        if CAT_OUT == 'LepLoD': CAT_INS.append('ttbblv')
        if CAT_OUT == 'LepHiD': CAT_INS.remove('ttbblv')
        if CAT_OUT == 'LepLoE': CAT_INS.append('ttbll')
        if CAT_OUT == 'LepHiE': CAT_INS.remove('ttbll')
        if CAT_OUT == 'LepLoF': CAT_INS.append('Zll')
        if CAT_OUT == 'LepHiF': CAT_INS.remove('Zll')
        if CAT_OUT == 'LepLoG': CAT_INS.append('ZvvHi')
        if CAT_OUT == 'LepHiG': CAT_INS.remove('ZvvHi')
        if CAT_OUT == 'LepLoH': CAT_INS.remove('ZvvLo')
        if CAT_OUT == 'LepHiH': CAT_INS.append('ZvvLo')
    ## End conditional: if CAT_OUT.startswith('Lep')
    elif CAT_OUT.endswith('Incl'):
        CAT_INS = [CAT_OUT.replace('Incl','')+sub for sub in ['Lo','Hi']]
    for cat in CAT_INS:
        CATS_IN[cat] = {}
        CATS_IN[cat]['sigs'] = [sig+'toaato4b' for sig in LEPSIGS]
        CATS_IN[cat]['dir']  = IN_DIR+cat
        if cat.startswith('Zll') or cat.startswith('ttbll'):
            CATS_IN[cat]['bkgs'] = ['Zll','ZZ','TT2l','STop_tW_12l','STbar_tW_12l','MC']  ## Put 'MC' at the end!
        elif cat.startswith('Wlv') or (cat.startswith('tt') and cat.endswith('lv')):
            CATS_IN[cat]['bkgs'] = ['Zll','ZZ','TT2l','STop_tW_12l','STbar_tW_12l','Wlv','TT1l','ST_s_1l','STop_t','STbar_t','QCD','MC']
        elif cat.startswith('Zvv'):
            CATS_IN[cat]['bkgs'] = ['Wqq','Zqq','TT0l','TT1l','Zvv','Zll','Wlv','ST_s_1l','STop_t','STbar_t','STop_tW_Incl','STbar_tW_Incl','WW','WZ','ZZ','MC']
        elif cat == 'tt0l1b':
            CATS_IN[cat]['bkgs'] = ['Wqq','Zqq','TT0l','TT1l']  ## Drop QCD, thus don't use existing 'MC'
        else:
            assert False, 'Category %s not a valid leptonic category!!! Quitting.' % cat
## End conditional: elif IS_LEP
else:
    assert False, '\nERROR!!! Specify valid CAT_OUT in merge_files_mctoy.py! (%s is invalid.)\n' % CAT_OUT


## For use as input to Haa4b_makeMCtoy.py
OUT_DIR = IN_DIR+'2D_in_merged_'+CAT_OUT+'/'+YEAR+'/'
## For use as input to htoaato4b_mctoy.py
OUT_DIRS = {}
WP_CUTS = {}
for cat in [CAT_OUT]+CAT_INS:
    OUT_DIRS[cat] = EOS_DIR+'/plots/'+DATE+'/'+cat+'/'+YEAR+'/'
    #if cat.startswith('gg0l') or cat.startswith('VBFjj'):
    if cat.startswith('gg0l'):
        WP_CUTS[cat] = ['WP40', 'WP60']  ## Use WP60 to model WP40
    elif cat.startswith('VBFjj'):
        WP_CUTS[cat] = ['WP40']  ## No WP60 for VBFjj available currently
    elif cat == 'VVBFjj':
        #WP_CUTS[cat] = ['WP4060','WP60']  ## VBFjjHi has WP60 to model WP40, Vjj only WP60
        WP_CUTS[cat] = ['WP4060']  ## VBFjjHi currently has only WP40, Vjj only WP60
    elif cat == 'VjjHi' and CAT_OUT == 'VVBFjj':
        WP_CUTS[cat] = ['WP40','WP60']  ## Create "false" WP40 (really still WP60) to add to VBFjj WP40
    else:
        WP_CUTS[cat] = ['WP60']  ## Default WP for most categories


def check_binning(h1, h2):
    nX1 = h1.GetNbinsX()
    nY1 = h1.GetNbinsY()
    nX2 = h2.GetNbinsX()
    nY2 = h2.GetNbinsY()
    xL1 = h1.GetXaxis().GetBinLowEdge(1)
    xH1 = h1.GetXaxis().GetBinLowEdge(nX1+1)
    yL1 = h1.GetYaxis().GetBinLowEdge(1)
    yH1 = h1.GetYaxis().GetBinLowEdge(nY1+1)
    xL2 = h2.GetXaxis().GetBinLowEdge(1)
    xH2 = h2.GetXaxis().GetBinLowEdge(nX2+1)
    yL2 = h2.GetYaxis().GetBinLowEdge(1)
    yH2 = h2.GetYaxis().GetBinLowEdge(nY2+1)
    if (nX1 != nX2 or nY1 != nY2 or xL1 != xL2 or xH1 != xH2 or yL1 != yL2 or yH1 != yH2):
        print('\nMAJOR ERROR!!! %s is %d x %d, %s is %d x %d' % (h1.GetName(), nX1, nY1,
                                                                 h2.GetName(), nX2, nY2))
        print('Spanning [%.1f-%.1f] x [%.1f-%.1f] vs. [%.1f-%.1f] x [%.1f-%.1f]' % (xL1, xH1, yL1, yH1,
                                                                                    xL2, xH2, yL2, yH2))
        sys.exit()
## End function: check_binning(h1, h2)


def main():

    print('\nInside merge_files_mctoy\n')

    print('\n\nWARNING!!! Should run from inside 2DAlphabet/CMSSW_11_3_4/src/2DAlphabet/')
    print('to avoid "list is accessing an object already deleted" error! - AWB 2024.06.24\n')
    print('See https://root-forum.cern.ch/t/error-in-tlist-clear-a-list-is-accessing-an-object-already-deleted-list-name-tlist-when-opening-a-file-created-by-root-6-30-using-root-6-14-09/57588/1')
    

    if not PRINTONLY and len(ONE_SAMP) == 0:
        print('\nDeleting any existing output directories, and creating empty ones:')
        for o_dir in [OUT_DIR]+[OUT_DIRS[cat] for cat in [CAT_OUT]+CAT_INS]:
            print(o_dir)
            if os.path.exists(o_dir):
                shutil.rmtree(o_dir)
            os.makedirs(o_dir)

    h_outs = {}  ## Save summed output histograms
    h_ins  = {}  ## Also save the inputs (keeps naming scheme consistent)
    all_systs = {}  ## Full list of systematics across all categories, by sample
    spikes = {}
    for cat in CAT_INS:
        if PRINTONLY: print('\n\n******* Category %s *******\n' % cat)
        ## Save quantities for S/B and S/sqrt(B) estimates
        data_pass,data_fail,data_fail_win = 0,0,0
        MC_pass,MC_fail,MC_fail_win,MC_pass_win = 0,0,0,0
        sig_pass,sig_pass_win = 0,0
        spikes[cat] = {}

        samps = ['Data']
        for bkg in CATS_IN[cat]['bkgs']:
            samps.append(bkg)
        samps.append('SumMC')  ## Summed background MC
        for mA in MASSESA:
            for sig in CATS_IN[cat]['sigs']:
                samps.append(sig+'_mA_'+mA)
            samps.append('SumHtoaato4b_mA_'+mA)
        for sampIn in samps:
            samp = sampIn
            if len(ONE_SAMP) > 0 and not ONE_SAMP in samp: continue
            if len(ONE_SAMP) > 0: print('Found %s matching %s!' % (samp, ONE_SAMP))
            spikes[cat][samp] = {}
            if not samp in all_systs.keys():
                all_systs[samp] = ['Nom'] if samp.startswith('Sum') else []
            for wp in WP_CUTS[cat]:
                if IS_LEP and not cat.startswith('Zvv') and not cat.startswith('tt0l'):
                    in_file_str = CATS_IN[cat]['dir']+'/%s/%s/%s_%s_%s.root' % (wp, YEAR, cat, samp, YEAR)
                else:
                    in_file_str = CATS_IN[cat]['dir']+'/%s/%s_%s_%s.root' % (YEAR, cat, samp, YEAR)
                in_file = None
                in_hists = []
                in_systs = ['Nom']
                spikes[cat][samp][wp] = {}
                ## SumHtoaato4b and SumMC are constructed on the fly
                if not samp.startswith('Sum'):
                    if VERBOSE or (samp == 'Data' and not PRINTONLY):
                        print('\n*******\nReading from %s' % in_file_str)
                    in_file = R.TFile(in_file_str, 'open')
                    in_hists_all = []
                    for key in in_file.GetListOfKeys():
                        if not key.GetName() in in_hists_all:
                            in_hists_all.append(key.GetName())
                    if len(in_hists_all) == 0:
                        print('*** WEIRD ERROR!!! %s has no histograms! Skipping. ***' % in_file_str)
                        continue
                    in_hists = [hst.replace('_Nom','') for hst in in_hists_all if hst.endswith('_Nom')]
                    in_systs = [hst.replace(in_hists[0]+'_','') for hst in in_hists_all if hst.startswith(in_hists[0])]
                    in_systs = sorted(in_systs, key=str.casefold)
                    in_systs.insert(0, in_systs.pop(in_systs.index('Nom')))
                    if VERBOSE:
                        print('  * %d histograms, %d systematic variations' % (len(in_hists), len(in_systs)))
                        if not 'Htoaato4b' in samp:
                            print('    (Only using nominal distribution for non-signal)')
                    if not 'Htoaato4b' in samp:
                        in_systs = ['Nom']
                    else:
                        with open('logs/systs_%s_%s_%s_%s.txt' % (cat, samp, wp, YEAR), 'w') as fsyst:
                            for syst in in_systs:
                                fsyst.write(syst+'\n')
                    all_systs[samp] = all_systs[samp]+[syst for syst in in_systs if not syst in all_systs[samp]]
                    all_systs[samp] = sorted(all_systs[samp], key= str.casefold)
                    all_systs[samp].insert(0, all_systs[samp].pop(all_systs[samp].index('Nom')))
                ## End conditional: if not samp.startswith('Sum')

                for mHr in MHREGS:
                    if PRINTONLY and mHr != 'pnet': continue
                    spikes[cat][samp][wp][mHr] = {}
                    for mAr in MAREGS:
                        if PRINTONLY and mAr != '34a': continue
                        spikes[cat][samp][wp][mHr][mAr] = {}
                        for pf in ['Pass', 'Fail']:
                            h_out_nom = None  ## Already-summed nominal histogram (for new systematics)
                            firstHist = True  ## Bool to track if first output hist needs to be created
                            spikes[cat][samp][wp][mHr][mAr][pf] = {}
                            for syst in in_systs:
                                catIn = cat
                                ## VBFjj category histograms currently named just VBF
                                if cat.startswith('VBFjj'):
                                    catIn = cat.replace('VBFjj','VBF')
                                h_in_name_read  = '%s_%s_%s_%s_%s_%s_%s_%s' % (catIn, samp, YEAR, mHr, mAr, wp, pf, syst)
                                h_in_name_write = '%s_%s_%s_%s_%s_%s_%s_%s' % (cat, samp, YEAR, mHr, mAr, wp, pf, syst)
                                #wp_out = 'WP4060' if (CAT_OUT == 'VVBFjj' and wp == 'WP40') else wp
                                wp_out = 'WP4060' if CAT_OUT == 'VVBFjj' else wp
                                assert (wp_out in WP_CUTS[CAT_OUT]), '\nERROR!!! %s wp = %s, wp_out = %s, not in WP_CUTS[%s]. Quitting.' % (cat, wp, wp_out, CAT_OUT)
                                h_out_base = '%s_%s_%s_%s_%s_%s_%s' % (CAT_OUT, samp, YEAR, mHr, mAr, wp_out, pf)
                                h_out_name = h_out_base+'_'+syst
                                if syst == 'Nom' and h_out_name in h_outs.keys():
                                    firstHist = False
                                    h_out_nom = h_outs[h_out_name].Clone('h_out_nom')
                                ## No real VjjHi WP40; use WP60 to add to VBFjjHi WP40 in VVBFjj
                                if wp == 'WP40' and cat == 'VjjHi':
                                    h_in_name_read = h_in_name_read.replace('_'+wp+'_', '_WP60_')

                                ## Get sums from previously accessed and saved histograms
                                if samp == 'SumMC':
                                    xBkg = CATS_IN[cat]['bkgs'][0]  ## First background MC component
                                    h_in = h_ins[h_in_name_write.replace('SumMC',xBkg)].Clone('SumMC')
                                    for iBkg in CATS_IN[cat]['bkgs'][1:]:
                                        if iBkg != 'MC' and iBkg != 'SumMC':
                                            h_in.Add(h_ins[h_in_name_write.replace('SumMC',iBkg)])
                                elif samp.startswith('SumHtoaato4b'):
                                    xSig = CATS_IN[cat]['sigs'][0]  ## First signal component
                                    h_in = h_ins[h_in_name_write.replace('SumHtoaato4b',xSig)].Clone('SumHtoaato4b')
                                    for iSig in CATS_IN[cat]['sigs'][1:]:
                                        h_in_name_iSig = h_in_name_write.replace('SumHtoaato4b',iSig)
                                        if h_in_name_iSig in h_ins.keys():
                                            h_in.Add(h_ins[h_in_name_iSig])
                                        else:
                                            print('*** WEIRD ERROR!!! %s histogram missing! Skipping. ***' % h_in_name_iSig)
                                    if VERBOSE or PRINTONLY:
                                        print('\n%s has integral %.1f' % (h_in_name_write, h_in.Integral()))
                                else: ## Standard behavior: get histogram from input file
                                    if VERBOSE: print('\nGetting histogram %s' % h_in_name_read)
                                    h_in = in_file.Get(h_in_name_read)
                                    if int(5 / h_in.GetXaxis().GetBinWidth(1)) != 1:
                                        ## VBF plots used to use 240 bins from [0, 240] for massH (fixed as of 2025_07_25)
                                        if VERBOSE or (sampIn == samps[0] and wp == WP_CUTS[cat][0] and pf == 'Pass'):
                                            print('\nRebinning x-axis by %d\n' % int(5 / h_in.GetXaxis().GetBinWidth(1)))
                                        h_in.Rebin2D(int(5 / h_in.GetXaxis().GetBinWidth(1)), 1)
                                    if int(1 / h_in.GetYaxis().GetBinWidth(1)) != 1:
                                        if VERBOSE or (sampIn == samps[0] and wp == WP_CUTS[cat][0] and pf == 'Pass'):
                                            print('\nRebinning y-axis by %d\n' % int(1 / h_in.GetYaxis().GetBinWidth(1)))
                                        h_in.Rebin2D(int(1 / h_in.GetYaxis().GetBinWidth(1)), 1)
                                    if VERBOSE: print('  * Integral = %.2f' % h_in.Integral())
                                    if samp.startswith('QCD'):
                                        h_max = h_in.GetMaximum()
                                        h_int = h_in.Integral()
                                        if h_max > 0.05*h_int:
                                            if VERBOSE:
                                                print('\n***** MANUAL ADJUSTMENT TO %s in %s!!! *****' % (samp, cat))
                                                print('%s has max %.2f, integral %.2f (%.2f%%)' % (h_in_name_read, h_max, h_int, 100*h_max/h_int))
                                            nX = h_in.GetNbinsX()
                                            nY = h_in.GetNbinsY()
                                            for iX in range(1, nX+1):
                                                for iY in range(1, nY+1):
                                                    h_bin = h_in.GetBinContent(iX,iY)
                                                    if h_bin < 0.05*h_int: continue
                                                    h_area = h_in.Integral(iX-3,iX+3,iY-3,iY+3) - h_bin
                                                    if VERBOSE:
                                                        print('Bin (%d,%d) = %.2f +/- %.2f' % (iX, iY, h_bin, h_in.GetBinError(iX,iY)))

                                                        print('7x7 surrounding integral is %.2f' % h_area)
                                                        print('Setting (%d,%d) to %.3f' % (iX, iY, max(h_area/48.0, h_int/(nX*nY))))
                                                    h_in.SetBinContent(iX,iY, h_area/48.0)
                                                    h_in.SetBinError(iX,iY, h_area/48.0)
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['name'] = h_in_name_write
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['iX'] = iX
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['iY'] = iY
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['int'] = h_int
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['Ni'] = h_bin
                                                    spikes[cat][samp][wp][mHr][mAr][pf]['Nf'] = max(h_area/48.0, h_int/(nX*nY))
                                                ## End loop: for iY in range(1, nY+1)
                                            ## End loop: for iX in range(1, nX+1)
                                        ## End conditional: if h_max > 0.05*h_int
                                    ## End conditional: if samp.startswith('QCD')
                                ## End conditional: if samp  == 'SumMC' / elif samp.startswith('SumHtoaato4b') / else

                                if not (h_in_name_write in h_ins.keys()):
                                    h_ins[h_in_name_write] = h_in.Clone(h_in_name_write)
                                    if VERBOSE:
                                        print('Cloned %s into %s' % (h_in_name_read, h_ins[h_in_name_write].GetName()))
                                else:
                                    assert False, '\nERROR!!! Trying to add %s to existing %s! Quitting.' % (h_in_name_read, h_in_name_write)
                                if VERBOSE: print('  * Integral = %.2f' % h_ins[h_in_name_write].Integral())
                                h_ins[h_in_name_write].SetDirectory(0) ## Save locally

                                ## Create new histogram if it does not already exist
                                if firstHist or (syst != 'Nom' and not h_out_name in h_outs.keys()):
                                    if VERBOSE: print('Creating %s' % h_out_name)
                                    if VERBOSE: print('  * Integral = %.2f' % h_in.Integral())
                                    h_outs[h_out_name] = h_in.Clone(h_out_name)
                                    h_outs[h_out_name].SetDirectory(0) ## Save locally
                                    ## If new systematic, add previous nominal histograms
                                    if not firstHist:
                                        if VERBOSE: print('  * Adding %.2f from previous Nom' % h_out_nom.Integral())
                                        check_binning(h_outs[h_out_name], h_out_nom)
                                        h_outs[h_out_name].Add(h_out_nom)
                                elif syst == 'Nom' and not h_out_name in h_outs.keys():
                                    print(h_outs.keys())
                                    assert False, '\nERROR!!! Found no %s in list above.' % h_out_name
                                ## Add histogram into existing histogram
                                elif h_out_name in h_outs.keys():
                                    if VERBOSE: print('Adding %.2f from %s to %s (with %.2f)' % (h_in.Integral(), h_in_name_read,
                                                                                                 h_out_name, h_outs[h_out_name].Integral()))
                                    check_binning(h_outs[h_out_name], h_in)
                                    h_outs[h_out_name].Add(h_in)
                                    ## Add nominal histogram into previous systematics if not in this category
                                    if syst == 'Nom' and 'Htoaato4b' in samp:
                                        for systA in all_systs[samp]:
                                            if systA in in_systs: continue
                                            if VERBOSE: print('Adding %.2f from %s to %s (with %.2f)' % (h_in.Integral(), h_in_name_read,
                                                                                                         h_out_base+'_'+systA, h_outs[h_out_base+'_'+systA].Integral()))
                                            check_binning(h_outs[h_out_base+'_'+systA], h_in)
                                            h_outs[h_out_base+'_'+systA].Add(h_in)
                                        ## End loop: for systA in all_systs[samp]
                                    ## End conditional: if syst == 'Nom'
                                else:
                                    assert False, 'Logic error! firstHist and/or h_out_name in h_outs.keys() neither true nor false.'
                                ## End conditional: firstHist or (syst != 'Nom' and not h_out_name in h_outs.keys()) / elif ...
                                nXi = h_in.GetNbinsX()
                                nYi = h_in.GetNbinsY()
                                iXw = [ii+1 for ii in range(nXi) if h_in.GetXaxis().GetBinLowEdge(ii+1) == 110][0]
                                jXw = [ii for ii in range(nXi) if h_in.GetXaxis().GetBinLowEdge(ii+1) == 140][0]
                                if (wp == 'WP40') or (not 'WP40' in WP_CUTS[cat]):
                                    if samp == 'Data':
                                        if VERBOSE or PRINTONLY:
                                            print('Adding %d to data: %s (%s)' % (h_in.Integral(), samp, h_in_name_read))
                                        if pf == 'Pass':
                                            data_pass += h_in.Integral()
                                        if pf == 'Fail':
                                            data_fail += h_in.Integral()
                                            data_fail_win += h_in.Integral(iXw, jXw, 1, nYi)
                                    if samp == 'SumMC':
                                        if VERBOSE or PRINTONLY:
                                            print('Adding %d to SumMC: %s (%s)' % (h_in.Integral(), samp, h_in_name_read))
                                        if pf == 'Pass':
                                            MC_pass += h_in.Integral()
                                            MC_pass_win += h_in.Integral(iXw, jXw, 1, nYi)
                                        if pf == 'Fail':
                                            MC_fail += h_in.Integral()
                                            MC_fail_win += h_in.Integral(iXw, jXw, 1, nYi)
                                    if 'Htoaato4b' in samp and '_mA_' in samp and not 'SumH' in samp:
                                        if pf == 'Pass' and syst == 'Nom':
                                            if VERBOSE or (PRINTONLY and '_mA_30' in samp):
                                                print('Adding %.2f to sig: %s (%s)' % (h_in.Integral(), samp, h_in_name_read))
                                            sig_pass += h_in.Integral()
                                            sig_pass_win += h_in.Integral(iXw, jXw, 1, nYi)
                                ## End conditional: if (wp == 'WP40') or (not 'WP40' in WP_CUTS[cat])

                                if PRINTONLY and not 'Htoaato4b' in samp and (samp == 'Data' or wp == 'WP60'):
                                    print('%s %s %s integral = %.2f' % (wp, pf, samp, h_in.Integral()))
                                    if h_in.GetMaximum() > 0.05*h_in.Integral() or samp == 'MC' or samp == 'SumMC':
                                        print('  - Max = %.2f (%.2f%%)' % (h_in.GetMaximum(), 100*h_in.GetMaximum()/h_in.Integral()))
                            ## End loop: for syst in in_systs
                            del h_out_nom
                        ## End loop: for pf in ['Pass', 'Fail']
                    ## End loop: for mAr in MAREGS
                ## End loop: for mHr in MHREGS
                if not samp.startswith('Sum'):
                    in_file.Close()

                if PRINTONLY: continue

                ## Common output ROOT file with all histograms (input to Haa4b_makeMCtoy.py)
                out_file_str = OUT_DIR+('%s_%s_%s.root' % (CAT_OUT, samp, YEAR))
                root_cmd = ('update' if os.path.exists(out_file_str) else 'recreate')
                out_file = R.TFile(out_file_str, root_cmd)
                ## ROOT file with only merged category histograms (input to htoaato4b_mctoy.py)
                out_file_str2 = OUT_DIRS[CAT_OUT]+('%s_%s_%s.root' % (CAT_OUT, samp, YEAR))
                root_cmd2 = ('update' if os.path.exists(out_file_str2) else 'recreate')
                out_file2 = R.TFile(out_file_str2, root_cmd2)
                if cat != CAT_OUT:
                    ## ROOT file with only individual category histograms (input to htoaato4b_mctoy.py)
                    out_file_str3 = OUT_DIRS[cat]+('%s_%s_%s.root' % (cat, samp, YEAR))
                    root_cmd3 = ('update' if os.path.exists(out_file_str3) else 'recreate')
                    out_file3 = R.TFile(out_file_str3, root_cmd3)

                if VERBOSE or 'Data' in out_file_str or len(ONE_SAMP) > 0:
                    print('\n*******\nWriting to %s' % out_file_str)
                    print('(Also to %s)' % out_file_str2)
                    if cat != CAT_OUT:
                        print('(Also to %s)' % out_file_str3)

                for mHr in MHREGS:
                    for mAr in MAREGS:
                        for pf in ['Pass', 'Fail']:
                            for syst in all_systs[samp]:
                                if not (syst == 'Nom' or 'Htoaato4b' in samp): continue
                                if syst in in_systs:
                                    ## Write out individual input histograms
                                    h_in_name = '%s_%s_%s_%s_%s_%s_%s_%s' % (cat, samp, YEAR, mHr, mAr, wp, pf, syst)
                                    out_file.cd()
                                    h_ins[h_in_name].Write()
                                    if cat != CAT_OUT:
                                        out_file3.cd()
                                        h_ins[h_in_name].Write()
                                    if VERBOSE or 'Sum' in samp: print('Wrote out %s' % h_in_name)
                                    if VERBOSE or 'Sum' in samp: print('  * Integral = %.2f' % h_ins[h_in_name].Integral())
                                ## End conditional: if syst in in_systs
                                ## Write out summed output histogram (overwrite if needed)
                                #wp_out = 'WP4060' if (CAT_OUT == 'VVBFjj' and wp == 'WP40') else wp
                                wp_out = 'WP4060' if CAT_OUT == 'VVBFjj' else wp
                                assert (wp_out in WP_CUTS[CAT_OUT]), '\nERROR!!! %s wp = %s, wp_out = %s, not in WP_CUTS[%s]. Quitting.' % (cat, wp, wp_out, CAT_OUT)
                                h_out_name = '%s_%s_%s_%s_%s_%s_%s_%s' % (CAT_OUT, samp, YEAR, mHr, mAr, wp_out, pf, syst)
                                out_file.cd()
                                h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                                out_file2.cd()
                                h_outs[h_out_name].Write('', R.TObject.kOverwrite)
                                if VERBOSE: print('Wrote out %s' % h_out_name)
                                if VERBOSE: print('  * Integral = %.2f' % h_outs[h_out_name].Integral())
                            ## End loop: for syst in all_systs[samp]
                        ## End loop: for pf in ['Pass', 'Fail']
                    ## End loop: for mAr in MAREGS
                ## End loop: for mHr in MHREGS
                out_file.Write()
                out_file.Close()
                out_file2.Write()
                out_file2.Close()
                if cat != CAT_OUT:
                    out_file3.Write()
                    out_file3.Close()
            ## End loop: for wp in WP_CUTS[cat]
            if 'Htoaato4b' in samp and not 'SumHtoaato4b' in samp:
                with open('logs/systs_%s_%s_%s.txt' % (CAT_OUT, samp, YEAR), 'w') as fsyst:
                    for syst in all_systs[samp]:
                        fsyst.write(syst+'\n')
        ## End loop: for sampIn in samps

        iWP = 'WP40' if 'WP40' in WP_CUTS[cat] else WP_CUTS[cat][0]
        if data_pass == 0:
            print('Very weird!!! %s data_pass = 0! Setting to 1.' % cat)
            data_pass = 1.0
        data_pass_win = data_fail_win*(data_pass/data_fail)
        MC_pass_win_est = MC_fail_win*(MC_pass/MC_fail)
        sig_pass     /= len(MASSESA)
        sig_pass_win /= len(MASSESA)
        print('\n*** %8s %s %s (%.2f fb-1) ***' % (YEAR, cat, iWP, LUMIS[YEAR])) 
        print('Data  pass/fail = %d/%d (%.2f%%), est. %.2f in Higgs window (%.2f%%)' % (data_pass, data_fail, 100*data_pass/data_fail, data_pass_win, 100*data_pass_win/data_pass))
        print('SumMC pass/fail = %.1f/%.1f (%.2f%%), est. %.2f in Higgs window (%.2f%%), %.2f obs.' % (MC_pass, MC_fail, 100*MC_pass/MC_fail, MC_pass_win_est, 100*MC_pass_win_est/MC_pass, MC_pass_win))
        print('12 - 60 GeV Signal pass = %.2f, %.2f in window (%.2f%%)' % (sig_pass, sig_pass_win, 100*sig_pass_win/max(sig_pass, 0.001)))
        print('S/B = %.2f, S/sqrt(B) = %.2f; %.2f sig in window, %.2f total data per 10 fb-1' % (sig_pass_win/data_pass_win, sig_pass_win/math.sqrt(data_pass_win), 10*sig_pass_win/LUMIS[YEAR], 10*(data_pass+data_fail)/LUMIS[YEAR]))
        if 'WP40' in WP_CUTS[cat]:
            print('S/B = %.2f, S/sqrt(B) = %.2f for 0.75 X4b SF' % (0.75*sig_pass_win/data_pass_win, 0.75*sig_pass_win/math.sqrt(data_pass_win)))

    ## End loop: for cat in CAT_INS

    print('\n\n\n***** SPIKE-SMOOTHING *****\n')
    for cat in spikes.keys():
        for samp in spikes[cat].keys():
            for wp in spikes[cat][samp].keys():
                for mHr in spikes[cat][samp][wp].keys():
                    for mAr in spikes[cat][samp][wp][mHr].keys():
                        for pf in spikes[cat][samp][wp][mHr][mAr].keys():
                            spk = spikes[cat][samp][wp][mHr][mAr][pf]
                            if len(spk.keys()) > 0:
                                print('%s %s %s %s %s %s (%s)' % (cat, samp, wp, mHr, mAr, pf, spk['name']))
                                print('Integral = %.2f, (%d,%d) = %.3f  --> %.3f' % (spk['int'], spk['iX'], spk['iY'], spk['Ni'], spk['Nf']))
    ## End loop: for cat in spikes.keys()



    print('\n\nAll done!')
    
## End function: def main()


if __name__ == '__main__':
    main()

