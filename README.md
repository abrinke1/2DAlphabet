# Running instructions
```
ssh -X -Y abrinke1@lxplus.cern.ch
./start_el7.sh
cd /afs/cern.ch/work/a/abrinke1/public/HiggsToAA/2DAlphabet/CMSSW_11_3_4/src/
cmsenv
source twoD-env/bin/activate
cd 2DAlphabet/
```

# Installation instructions
```
## Follow instructions to create start_el7.sh script
## https://gitlab.cern.ch/cms-cat/cmssw-lxplus#usage
./start_el7.sh
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v9.1.0
cd ../../
git clone git@github.com:JHU-Tools/CombineHarvester.git
cd CombineHarvester/
git fetch origin
git checkout CMSSW_11_3_X
cd ../
scramv1 b clean
scramv1 b -j 8

git clone https://github.com/JHU-Tools/2DAlphabet.git
python3 -m virtualenv twoD-env
source twoD-env/bin/activate
cd 2DAlphabet/
git fetch origin
git checkout py3
python setup.py develop

```

# Toy generation with Condor
```
## Setup config/user.config file with EOS output directory
./config/user.sh
## Fetch data and MC files with 2DAlphabet input (~5 minutes)
./fetchtoyinput.sh
## Temporary hack to fix missing VBFHtoaato4b_mA_55 files in 2016postVFP
python3 macros/duplicate_files.py
## Merge histograms into categories, including merging systematics
## Takes 20 - 30 minutes per category per year, so adjust "for YEAR in XXXX"
##   loop to contain a single year, then run 4 years in 4 separate lxplus sessions
## Takes ~1.5 hours; could run separate categories in separate sessions as well,
##   or run merge_files_mctoy.py with "&" at the end to run in the background
## In any case, need to make sure all merging is done before running merge_years_mctoy.py
./mergetoyinput.sh
## Merge 4 eras into Run2 (5 - 10 minutes for 5 standard categories)
python3 merge_years_mctoy.py
## Generate toys from smoothed data and MC, including background-only and signal-injected
## Can adjust number of toys (NTOYS) and list of categories (CATS) in generatetoys.sh
## Can adjust choice of mass regressors (MHREG, MAREG) and signal injection (SIGINJ) in Haa4b_makeMCtoy.py
./generatetoys.sh
## Can also run a single toy generation job manually as follows,
## where "CAT" is the category name and "SOURCE" is Data or MC
python3 Haa4b_makeMCtoy.py CAT NTOYS SOURCE
## Create 2DAlphabet workspace and run fits for a single toy
## Outputs to output/MCtoys/Mergecards or output/Datatoys/Mergecards
## If toy index >= 0, outputs to EOS directory
## ./run_toy.sh [toy index] [Data or MC] [Category] [signal mA] [fit] [signal injection]
./run_toy.sh -1 MC gg0lV 12 2s2C false
## Create 2DAlphabet workspaces and run fits for many toys
## First adjust FIT, and iCat and iDM and iMA and SINJ loops as desired
## First run mA=12 jobs to create workspaces; when these are done can run all other mass points
cd Condor
./runCondor_toys.sh
condor_q [username]
cd ..
## Plot best-fit-mu and pull value histograms from toys
## First adjust DMC, SIGINJ, CATS, MASSESA, and FITS as desired 
python3 macros/Haa4b_MultiDim_summary.py
## Print expected and observed limits from "rounded" background templates
## First adjust SIGINJ and mA, DMC, cat, and fit loops as desired
python3 macros/Haa4b_Limit_printout.py
## Should add macro to assess Goodness-of-Fit from mA=12 ROOT files
## Should add macro to plot distributions of expected and observed limits from toys
```
