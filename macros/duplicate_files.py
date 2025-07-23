#! /usr/bin/env python
## Script to duplicate files in case of missing files

import os
import ROOT as R

IN_DIR_A = '/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/raw_inputs/2025_07_14/'
IN_DIR_B = '/eos/cms/store/user/abrinke1/HiggsToAA/2DAlphabet/plots/2025_07_14/'
YEAR_A = '2016preVFP'
YEAR_B = '2016postVFP'
SAMP = 'VBFHtoaato4b_mA_55'

def main():

    print('\nRunning duplicate_files\n')

    print('\nWARNING!!! Should run from inside 2DAlphabet/CMSSW_11_3_4/src/2DAlphabet/')
    print('to avoid "list is accessing an object already deleted" error! - AWB 2024.06.24\n')
    print('See https://root-forum.cern.ch/t/error-in-tlist-clear-a-list-is-accessing-an-object-already-deleted-list-name-tlist-when-opening-a-file-created-by-root-6-30-using-root-6-14-09/57588/1')

    for top_dir in [IN_DIR_A, IN_DIR_B]:
        print('\n\n*** Duplicating files in %s ***' % top_dir)
        for o_dir in [top_dir+sub_dir for sub_dir in os.listdir(top_dir)]:
            if '/Zll' in o_dir or '/Wlv' in o_dir or '/ttb' in o_dir:
                continue  ## Skip leptonic directories
            in_dir_A = o_dir+'/'+YEAR_A+'/'
            f_list_A = [in_dir_A+fl for fl in os.listdir(in_dir_A) if SAMP in fl]
            for fn_A in f_list_A:
                fn_B = fn_A.replace(YEAR_A, YEAR_B)
                print('Copying %s into %s' % (fn_A, fn_B))
                f_A = R.TFile(fn_A, 'open')
                hns_A = [key.GetName() for key in f_A.GetListOfKeys()]
                print('  * %d histograms' % len(hns_A))
                f_B = R.TFile(fn_B, 'recreate')
                f_B.cd()
                for hn_A in hns_A:
                    hn_B = f_A.Get(hn_A).Clone(hn_A.replace(YEAR_A, YEAR_B))
                    hn_B.Write()
                    del hn_B
                f_B.Write()
                f_B.Close()
                del f_B
                f_A.Close()
                del f_A
                ## End loop: for hn_A inhns_A
            ## End loop: for fn_A in f_list_A
        ## End loop: for o_dir in [top_dir+sub_dir for sub_dir in os.listdir(top_dir)]
    ## End loop: for top_dir in [IN_DIR_A, IN_DIR_B]

    print('\n\nAll done!')

## End function: def main()

if __name__ == '__main__':
    main()
