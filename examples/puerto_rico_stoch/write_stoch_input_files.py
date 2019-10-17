from __future__ import print_function
import os
import shutil
import temoatools as tt

# Baseline databases to use
dbs = ["WA.sqlite", "WB.sqlite", "WC.sqlite", "WD.sqlite",
       "XA.sqlite", "XB.sqlite", "XC.sqlite", "XD.sqlite",
       "YA.sqlite", "YB.sqlite", "YC.sqlite", "YD.sqlite",
       "ZA.sqlite", "ZB.sqlite", "ZC.sqlite", "ZD.sqlite"]

# model years
years = [2016, 2021, 2026, 2031, 2036]

# Hurricane scenarios with corresponding probabilities and windspeeds
scenarios = ["H1", "H2", "H3"]
probabilities_hist = [0.56, 0.24, 0.2]  # sum must equal 1
probabilities_climate_change = [0.16, 0.24, 0.6]  # sum must equal 1
windspeeds = [20.0, 50.0, 150.0]  # mph

# temoa model technologies and corresponding fragility curve groups
techs = {'LOCAL': "inf_stiff", 'UGND_TRANS': "UGND", 'UGND_DIST': "UGND", 'TRANS': "trans", 'SUB': "sub",
         'DIST_COND': "dist_cond", 'DIST_TWR': "dist_twr", 'EX_SOLPV': "solar", 'EC_SOLPV': "solar",
         'ED_SOLPV': "solar", 'EX_WIND': "wind", 'EC_WIND': "wind", 'ED_WIND': "wind", 'EX_COAL': "coal_biomass",
         'EC_BIO': "coal_biomass", 'ED_BIO': "coal_biomass", 'EX_NG_CC': "natgas_petrol", 'EC_NG_CC': "natgas_petrol",
         'EC_NG_OC': "natgas_petrol", 'ED_NG_CC': "natgas_petrol", 'ED_NG_OC': "natgas_petrol",
         'EX_DSL_SIMP': "natgas_petrol", 'EX_DSL_CC': "natgas_petrol", 'EX_OIL_TYPE1': "natgas_petrol",
         'EX_OIL_TYPE2': "natgas_petrol", 'EX_OIL_TYPE3': "natgas_petrol", 'EX_MSW_LF': "natgas_petrol",
         'EX_HYDRO': "hydro", 'EC_BATT': "battery", 'ED_BATT': "battery"}

curves = {"inf_stiff": "inf_stiff",
                "trans": "trans_UK_base",
                "sub": "sub_HAZUS_severe_k3",
                "dist_cond": "dist_cond_TX",
                "dist_twr": "dist_60yr",
                "wind": "wind_nonyaw",
                "solar": "solar_utility",
                "coal_biomass": "secbh_severe",
                "natgas_petrol": "secbm_severe",
                "battery": "secbl_severe",
                "hydro": "cecbl_severe",
                "UGND":"secbl_severe"}

# Create directory to store outputs
wrkdir = os.getcwd()
stochdir = wrkdir + "\\stoch_inputs"
try:
    os.stat(stochdir)
except:
    os.mkdir(stochdir)
os.chdir(stochdir)

n_cases = 1
for case in range(n_cases):
    # historical probabilities
    if case == 0:
        probabilities = probabilities_hist

    # climate change probabilities
    elif case == 1:
        probabilities = probabilities_climate_change

    # Iterate through each database for each case
    for db in dbs:
        db_name = tt.remove_ext(db)

        # ====================================
        # Stochastic input file
        # ====================================
        # Write File
        filename = "stoch_" + db_name + "_" + str(case) + ".py"
        # Open File
        f = open(filename, "w")
        f.write(
            "# Automatically generated stochastic input file from temoatools github.com/EnergyModels/temoatools\n\n")
        f.write("verbose = True\n")
        f.write("force = True\n")
        f.write("\n")
        f.write("dirname = '" + db_name + "_" + str(case) + "'\n")  # Update
        f.write("modelpath = '../temoa_model/temoa_model.py'\n")
        f.write("dotdatpath = '../data_files/" + db_name + "_" + str(case) + ".dat'\n")  # Need to check
        f.write("stochasticset = 'time_optimize'\n")
        f.write("stochastic_points = (")
        for year in years:
            f.write(str(year) + ", ")
        f.write(")\n")
        f.write("stochastic_indices = {'CapReduction': 0}\n")
        f.write("types = (\n\t")
        for scenario in scenarios:
            f.write("'" + scenario + "', ")
        f.write("\n")
        f.write(")\n")
        f.write("conditional_probability = dict(\n")
        for scenario, prob in zip(scenarios, probabilities):
            f.write("\t" + scenario + "=" + str(prob) + ",\n")
        f.write(")\n")
        f.write("rates = {\n")
        f.write("\t'CapReduction': dict(\n")
        for scenario, prob, windspeed in zip(scenarios, probabilities, windspeeds):
            f.write("\t\t" + scenario + "=(\n")
            for tech in techs.keys():
                tech_cat = techs[tech]
                curve = curves[tech_cat]
                fragility = tt.fragility(windspeed, curve=curve)
                capReduction = round(1.0 - fragility, 3)
                f.write("\t\t\t('" + tech + "', " + str(capReduction) + "),\n")
            f.write("\t\t),\n\n")
        f.write("\t),\n")
        f.write("}\n")

        # Close File
        f.close()

        # ====================================
        # Configuration file
        # ====================================
        filename = "config_stoch_" + db_name + "_" + str(case) + ".txt"
        temoa_path = "C:\\temoa_stochastic"
        f = open(filename, "w")
        # ---
        f.write(
            "#-----------------------------------------------------                                                          \n")
        f.write(
            "# This is an automatically generated configuration file for Temoa using temoatools github.com/EnergyModels/temoatools\n")
        f.write("# It allows you to specify (and document) all run-time model options\n")
        f.write("# Legal chars in path: a-z A-Z 0-9 - _ \ / . :\n")
        f.write("# Comment out non-mandatory options to omit them\n")
        f.write("#----------------------------------------------------- \n")
        f.write("\n")
        f.write("# Input File (Mandatory)\n")
        f.write("# Input can be a .sqlite or .dat file\n")
        f.write("# Both relative path and absolute path are accepted\n")
        f.write("--input=" + temoa_path + "\\tools\\" + db_name + "_" + str(case) + "\\ScenarioStructure.dat\n")
        f.write("\n")
        f.write("# Output File (Mandatory)\n")
        f.write("# The output file must be a existing .sqlite file\n")
        f.write("--output=" + temoa_path + "\\data_files\\" + db_name + "_" + str(case) + ".sqlite\n")
        f.write("\n")
        f.write("# Scenario Name (Mandatory)\n")
        f.write("# This scenario name is used to store results within the output .sqlite file\n")
        f.write("--scenario=" + db_name + "_" + str(case) + "\n")
        f.write("\n")
        f.write("# Path to the 'db_io' folder (Mandatory)\n")
        f.write("# This is the location where database files reside\n")
        f.write("--path_to_db_io=data_files\n")
        f.write("\n")
        f.write("# Spreadsheet Output (Optional)\n")
        f.write("# Direct model output to a spreadsheet\n")
        f.write("# Scenario name specified above is used to name the spreadsheet\n")
        f.write("#--saveEXCEL\n")
        f.write("\n")
        f.write("# Save the log file output (Optional)\n")
        f.write("# This is the same output provided to the shell\n")
        f.write("#--saveTEXTFILE\n")
        f.write("\n")
        f.write("# Solver-related arguments (Optional)\n")
        f.write("--solver=cplex                    # Optional, indicate the solver\n")

        f.write("#--keep_pyomo_lp_file             # Optional, generate Pyomo-compatible LP file\n")
        f.write("\n")
        f.write("# Modeling-to-Generate Alternatives (Optional)\n")
        f.write(
            "# Run name will be automatically generated by appending '_mga_' and iteration number to scenario name\n")
        f.write("#--mga {\n")
        f.write("#	slack=0.1                     # Objective function slack value in MGA runs\n")
        f.write("#	iteration=4                   # Number of MGA iterations\n")
        f.write(
            "#	weight=integer                # MGA objective function weighting method, currently 'integer' or 'normalized'\n")
        f.write("#}\n")
        f.write("\n")
        f.close()

# Copy baseline databases
for db in dbs:
    for case in range(n_cases):
        db_name = tt.remove_ext(db)
        # .sqlite
        src_dir = wrkdir + "\\databases\\" + db_name + ".sqlite"
        dst_dir = wrkdir + "\\stoch_inputs\\" + db_name + "_" + str(case) + ".sqlite"
        shutil.copy(src_dir, dst_dir)
        # .dat
        src_dir = wrkdir + "\\databases\\" + db_name + ".dat"
        dst_dir = wrkdir + "\\stoch_inputs\\" + db_name + "_" + str(case) + ".dat"
        shutil.copy(src_dir, dst_dir)

# Return to original working directory
os.chdir(wrkdir)
