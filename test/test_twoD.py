import pytest
import ROOT, os
from TwoDAlphabet.twoDalphabet import TwoDAlphabet
from TwoDAlphabet.helpers import execute_cmd

class TestTwoD():
    @classmethod
    def setup_class(cls):
	cls.twoD = TwoDAlphabet(
	    tag='test/unit_test/test_twoD',
	    inJSON='test/twoDtest.json',
	    findreplace={},  # should already be tested by test/test_config.py
	    externalOpts={"plotTemplateComparisons":"true"},
	    loadPrevious=False
	)
	cls.tag = cls.twoD.tag

    '''
    def test__save(self):
	self.twoD.Save()
	assert os.path.exists('')
    '''

    def test__init(self):
	assert self.twoD.options.plotTemplateComparisons == 'true'
	assert os.path.isdir('test/unit_test/test_twoD/')
	assert os.path.exists('test/unit_test/test_twoD/runConfig.json')
	assert os.path.isdir('test/unit_test/test_twoD/UncertPlots/')

    def test_load(self):
	test = TwoDAlphabet(
	    tag='test/unit_test/test_twoD',
	    inJSON='test/unit_test/test_twoD/runConfig.json',
	    findreplace={},
	    externalOpts={},
	    loadPrevious=True
	)
	assert test.workspace == None

    #def test__initQCD(self):
	 
