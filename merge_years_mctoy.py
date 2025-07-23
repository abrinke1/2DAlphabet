#! /usr/bin/env python
## Script to add merge_files_mctoy.py output from 4 eras into "Run2"

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
VVERBOSE = False
DATE  = '2025_07_14'
YEARS = ['2016preVFP','2016postVFP','2017','2018']
YRX = YEARS[-1]
#CATS = []  ## If empty, merge all categories
CATS = ['LepHiT','LepLo','HadXLo','gg0lIncl']

eos_from_config = [eos for eos in (open('config/user.config','r')).readlines() if eos.startswith('EOS_DIR=')]
EOS_DIR = eos_from_config[0].replace('EOS_DIR=','').replace('\n','')
IN_DIR_A = EOS_DIR+'/raw_inputs/%s/' % DATE
IN_DIR_B = EOS_DIR+'/plots/%s/' % DATE


def main():

    print('\nRunning merge_years_mctoy\n')

    print('\nWARNING!!! Should run from inside 2DAlphabet/CMSSW_11_3_4/src/2DAlphabet/')
    print('to avoid "list is accessing an object already deleted" error! - AWB 2024.06.24\n')
    print('See https://root-forum.cern.ch/t/error-in-tlist-clear-a-list-is-accessing-an-object-already-deleted-list-name-tlist-when-opening-a-file-created-by-root-6-30-using-root-6-14-09/57588/1')
    
    for top_dir in [IN_DIR_A, IN_DIR_B]:
        print('\n\n*** Merging categories in %s ***' % top_dir)
        for o_dir in [top_dir+sub_dir for sub_dir in os.listdir(top_dir)]:
            #do_merge = (len(CATS) == 0)
            do_merge = True
            for cat in CATS:
                if cat in o_dir.replace(top_dir,''):
                    #do_merge = True
                    do_merge = False
            if not do_merge:
                continue
            RAW_IN = ('/raw_inputs/' in o_dir and not '2D_in_merged_' in o_dir)
            ## Raw input files in leptonic categories have X4b WP sub-directory
            if RAW_IN and ('/Zll' in o_dir or '/Wlv' in o_dir or '/ttb' in o_dir):
                WP = '/WP40' if ('gg0l' in o_dir or 'VBF' in o_dir) else '/WP60'
                o_dir = o_dir+WP
            o_dir = o_dir+'/Run2/'
            print('\nCreating '+o_dir)
            if os.path.exists(o_dir):
                shutil.rmtree(o_dir)
            os.makedirs(o_dir)

            ## Get list of files for each year, and confirm there is the same number
            f_list = {}
            for yr in YEARS:
                in_dir = o_dir.replace('/Run2/','/'+yr+'/')
                f_list[yr] = [in_dir+fl for fl in os.listdir(in_dir) if fl.endswith('.root')]
            for yrA in YEARS:
                for yrB in YEARS:
                    assert len(f_list[yrA]) == len(f_list[yrB]), '%s has %d files, %s has %d files! (%s vs. %s)' % (yrA, len(f_list[yrA]), yrB, len(f_list[yrB]), f_list[yrA][0], f_list[yrB][0])
            f_list['Run2'] = [fl.replace(YRX,'Run2') for fl in f_list[YRX]]
            if VERBOSE: print('  * Found %d files' % len(f_list['Run2']))

            ## Loop over files
            nHistTot = 0
            for fn_out in f_list['Run2']:
                f_ins = {}
                hn_ins = {}
                ## Get list of histograms for each year, and confirm there is the same number
                for yr in YEARS:
                    fn_in = fn_out.replace('/Run2/', '/'+yr+'/').replace('Run2.root', yr+'.root')
                    f_ins[yr] = R.TFile(fn_in, 'open')
                    hn_ins[yr] = {}
                    hn_ins[yr]['Nom'],hn_ins[yr]['Sys'],hn_ins[yr]['SysYr'] = [],[],[]
                    hn_in_list = []
                    for key in f_ins[yr].GetListOfKeys():
                        if not key.GetName() in hn_in_list:
                            hn_in_list.append(key.GetName())
                    for hn_in in hn_in_list:
                        if hn_in.endswith('_Nom'):
                            hn_ins[yr]['Nom'].append(hn_in)
                    ## Only include systematics for signal MC
                    if 'Htoaato4b' in fn_in:
                        for hn_in in hn_in_list:
                            if hn_in.endswith('_Nom'): continue
                            ## Check that base histogram name exists in nominal form
                            for pf in ['Pass','Fail']:
                                if not '_'+pf+'_' in hn_in: continue
                                hn_pref = hn_in.split('_'+pf+'_')[0]
                                assert hn_pref+'_'+pf+'_Nom' in hn_ins[yr]['Nom'],  hn_pref+'_'+pf+'_Nom not found in '+fn_in
                                if yr[0:4] in hn_in.replace(hn_pref+'_'+pf+'_',''):
                                    hn_ins[yr]['SysYr'].append(hn_in)
                                else:
                                    hn_ins[yr]['Sys'].append(hn_in)
                    ## End conditional: if 'Htoaato4b' in fn_in
                    if VVERBOSE:
                        print('    - %s has %d Nom histograms' % (fn_in, len(hn_ins[yr]['Nom'])))
                        if 'Htoaato4b' in fn_in and not 'Htoaato4b' in fn_in:
                            print('      (also %d Sys and %d SysYr histograms)' % (len(hn_ins[yr]['Sys']), len(hn_ins[yr]['SysYr'])))
                ## End loop: for yr in YEARS
                match_nHist = True
                for yrA in YEARS:
                    for yrB in YEARS:
                        for suff in ['Nom','Sys']:
                            if len(hn_ins[yrA][suff]) != len(hn_ins[yrB][suff]):
                                print(hn_ins[yrA][suff])
                                print('***************')
                                print(hn_ins[yrB][suff])
                                assert False, '%s has %d %s hists, %s has %d!' % (fn_out.replace('Run2',yrA), len(hn_ins[yrA][suff]), suff, fn_out.replace('Run2',yrB), len(hn_ins[yrB][suff]))

                ## Create output file and fill with summed histograms from each year
                ## For signal, some systematics will be specific to each year
                if VERBOSE: print('    - Creating file %s' % fn_out)
                f_out = R.TFile(fn_out, 'recreate')
                f_out.cd()

                ## First sum nominal and common systematic histograms from all years
                nHist = 0
                for hn_in in hn_ins[YRX]['Nom']+hn_ins[YRX]['Sys']:
                    try:
                        h_out = f_ins[YRX].Get(hn_in).Clone(hn_in.replace(YRX,'Run2'))
                    except:
                        assert False, 'Could not find %s in %s' % (hn_in, f_ins[YRX].GetName())
                    for yr in YEARS[0:-1]:
                        hn_in_yr = hn_in.replace(YRX,yr)
                        try:
                            h_out.Add(f_ins[yr].Get(hn_in_yr))
                        except:
                            assert False, 'Could not find %s in %s' % (hn_in_yr, f_ins[yr].GetName())
                    h_out.Write()
                    del h_out
                    nHist += 1
                ## End loop: for hn_in in hn_ins[YRX]['Nom']+hn_ins[YRX]['Sys']
                nHistTot += nHist

                ## For per-year systematics, add one year to nominal from others
                for yr in YEARS:
                    for hn_in in hn_ins[yr]['SysYr']:
                        for pf in ['Pass','Fail']:
                            if not '_'+pf+'_' in hn_in: continue
                            hn_pref = hn_in.split('_'+pf+'_')[0]
                            assert hn_pref+'_'+pf+'_Nom' in hn_ins[yr]['Nom'],  hn_pref+'_'+pf+'_Nom not found in '+f_ins[yr].GetName()
                            hn_suff = hn_in.replace(hn_pref+'_'+pf,'')
                            hn_pref = hn_pref.replace('_'+yr+'_','_Run2_')
                            hn_out = hn_pref+'_'+pf+hn_suff
                            assert '_Run2_' in hn_out, '%s failed to replace %s, got %s' % (hn_in, yr, hn_out)
                            try:
                                h_out = f_ins[yr].Get(hn_in).Clone(hn_out)
                            except:
                                assert False, 'Could not find %s in %s' % (hn_in, f_ins[yr].GetName())
                            for yrB in YEARS:
                                if yrB == yr: continue
                                hn_inB = hn_out.replace(hn_suff,'').replace('_Run2_','_'+yrB+'_')
                                hn_inB = hn_inB+'_Nom'
                                try:
                                    h_out.Add(f_ins[yrB].Get(hn_inB))
                                except:
                                    assert False, 'Could not find %s in %s' % (hn_inB, f_ins[yrB].GetName())
                            h_out.Write()
                            del h_out
                            nHist += 1
                        ## End loop: for pf in ['Pass','Fail']
                    ## End loop: for hn_in in hn_ins[yr]['SysYr']
                ## End loop: for yr in YEARS

                f_out.Write()
                f_out.Close()
                del f_out
                for yr in YEARS:
                    f_ins[yr].Close()
                if VERBOSE: print('    - Wrote %s histograms to %s' % (nHist, fn_out))

            ## End loop: for fn_out in f_list['Run2']

            print('\nAdded %d files and %d histograms in %s' % (len(f_list['Run2']), nHistTot, o_dir))

        ## End loop: for o_dir in [top_dir+sub_dir for sub_dir in os.listdir(top_dir)]
        print('\n*** Done with categories in %s ***\n' % top_dir)
    ## End loop: for top_dir in [IN_DIR_A, IN_DIR_B]

    print('\n\nAll done!')
    
## End function: def main()

if __name__ == '__main__':
    main()

