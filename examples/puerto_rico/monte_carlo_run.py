import temoatools as tt

modelInputs_XLSX        = 'data.xlsx'
scenarioInputs          = 'scenarios.xlsx'
scenarioNames           = ['A','B','C','D']
paths                   = 'paths.csv'
sensitivityInputs       = 'sensitivityVariables.xlsx'
sensitivityMultiplier   = 10.0 # percent perturbation
n_cases = 7

tt.run_monte_carlo(modelInputs_XLSX, scenarioInputs, scenarioNames, paths, sensitivityInputs, sensitivityMultiplier,n_cases,path='data')