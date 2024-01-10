import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
generator = cms.EDFilter('Pythia8ConcurrentGeneratorFilter',
                        maxEventsToPrint = cms.untracked.int32(1),
                        pythiaPylistVerbosity = cms.untracked.int32(1),
                        filterEfficiency = cms.untracked.double(1.0),
                        pythiaHepMCVerbosity = cms.untracked.bool(False),
                        comEnergy = cms.double(13000.),
                        PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'ExcitedFermion:qqbar2tauStartau = on',
            'ExcitedFermion:Lambda= 10000',
            '4000015:onMode = off',
            '4000015:onIfMatch = 24 12',
            '4000015:onIfMatch = 24 14',
            '4000015:onIfMatch = 24 16',
            '4000015:m0 = 5500'),
                        parameterSets = cms.vstring('pythia8CommonSettings',
                                                    'pythia8CP5Settings',
                                                    'processParameters',
                                                    )))
