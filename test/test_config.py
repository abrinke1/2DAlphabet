import pytest
import numpy as np
from TwoDAlphabet.config import *

class TestConfig():
    @classmethod
    def setup_class(cls):
	cls.BaseConfig = Config('test/twoDtest.json', findreplace={})
	cls.FindReplace = Config('test/twoDtest.json',findreplace={"ttbar_16":"THIS","lumi":"IS"})

    def test__init(self):
	assert self.BaseConfig.config["PROCESSES"]["data_obs"]["LOC"] == "test/data/THselection_$process.root:MthvMh_particleNet_$region__nominal"

    def test__findreplace(self):
	assert "THIS" in self.FindReplace.config["PROCESSES"].keys()
	assert "IS" in self.FindReplace.config["SYSTEMATICS"].keys()

    def test__section(self):
	options = self.BaseConfig._section("OPTIONS")
	procs = self.BaseConfig._section("PROCESSES")
	assert options["plotUncerts"] == False
	assert procs["data_obs"]["SYSTEMATICS"] == []
	assert procs["ttbar_16"]["SCALE"] == 1.0
	assert procs["ttbar_16"]["LOC"] == "test/data/THselection_$process.root:MthvMh_particleNet_$region__nominal"

    def test__addFindReplace(self):
	with pytest.raises(ValueError):
	    Config('test/twoDtest.json',findreplace={"HIST":"this will raise ValueError"})

    def test__varReplacement(self):
	pass # Test done in constructor of cls.FindReplace

    def test__SaveOut(self):
	if os.path.exists('test/unit_test/CR/runConfig.json'):
	    os.remove('test/unit_test/CR/runConfig.json')
	self.BaseConfig.SaveOut('test/unit_test/CR/')
	assert os.path.exists('test/unit_test/CR/runConfig.json')

    def test__FullTable(self):
	df = self.BaseConfig.FullTable()
	assert df['process'].to_dict() == {
		0: 'data_obs', 1: 'ttbar_16', 2: 'ttbar_16', 3: 'ttbar_16',
		4: 'ttbar_16', 5: 'ttbar_16', 6: 'TprimeB-1800_16',
		7: 'TprimeB-1800_16', 8: 'TprimeB-1800_16', 9: 'TprimeB-1800_16',
                10: 'data_obs', 11: 'ttbar_16', 12: 'ttbar_16', 13: 'ttbar_16',
                14: 'ttbar_16', 15: 'ttbar_16', 16: 'TprimeB-1800_16',
                17: 'TprimeB-1800_16', 18: 'TprimeB-1800_16', 19: 'TprimeB-1800_16'
	}
	assert df['region'].to_dict() == {i:'CR_fail' if i < 10 else 'CR_pass' for i in range(20)}
	assert df['binning'].to_dict() == {i:'default' for i in range(20)}
	assert df['color'].to_dict() == {i:1 if i in [0,6,7,8,9,10,16,17,18,19] else 2 for i in range(20)}
        assert df['process_type'].to_dict() == {
                0: 'DATA', 1: 'BKG', 2: 'BKG', 3: 'BKG',
                4: 'BKG', 5: 'BKG', 6: 'SIGNAL',
                7: 'SIGNAL', 8: 'SIGNAL', 9: 'SIGNAL',
                10: 'DATA', 11: 'BKG', 12: 'BKG', 13: 'BKG',
                14: 'BKG', 15: 'BKG', 16: 'SIGNAL',
                17: 'SIGNAL', 18: 'SIGNAL', 19: 'SIGNAL'
        }
	assert df['scale'].to_dict() == {i:1.0 for i in range(20)}
	assert df['variation'].to_dict() == {
                0: 'nominal', 1: 'nominal', 2: 'lumi', 3: 'TT_xsec',
                4: 'JER', 5: 'JER', 6: 'nominal',
                7: 'lumi', 8: 'JER', 9: 'JER',
                10: 'nominal', 11: 'nominal', 12: 'lumi', 13: 'TT_xsec',
                14: 'JER', 15: 'JER', 16: 'nominal',
                17: 'lumi', 18: 'JER', 19: 'JER'
	}
	print(df['variation'])
	assert df['source_filename'].to_dict() == {
		0: 'test/data/THselection_Data_Run2.root', 
		10: 'test/data/THselection_Data_Run2.root', 
		6: 'test/data/THselection_TprimeB-1800_16.root', 
		7: 'test/data/THselection_TprimeB-1800_16_JER_up.root',
                8: 'test/data/THselection_TprimeB-1800_16_JER_down.root', 
		9: 'test/data/THselection_TprimeB-1800_16.root',
                16: 'test/data/THselection_TprimeB-1800_16.root', 
		17: 'test/data/THselection_TprimeB-1800_16_JER_up.root',
                18: 'test/data/THselection_TprimeB-1800_16_JER_down.root', 
		19: 'test/data/THselection_TprimeB-1800_16.root',
                1: 'test/data/THselection_ttbar_16.root', 
		2: 'test/data/THselection_ttbar_16.root',
                3: 'test/data/THselection_ttbar_16.root', 
		4: 'test/data/THselection_ttbar_16.root',
                5: 'test/data/THselection_ttbar_16.root', 
		11: 'test/data/THselection_ttbar_16.root',
                12: 'test/data/THselection_ttbar_16.root', 
		13: 'test/data/THselection_ttbar_16.root',
                14: 'test/data/THselection_ttbar_16.root', 
		15: 'test/data/THselection_ttbar_16.root'
	}
