import csv
import numpy as np
import scipy.stats as stats

def sampling_pmf(names, groups, p):
	"""
	Compute the likelihood ratio of the most likely group relative to the least likely group. 
	"""
	for name in names:
		groups[name]["pmf"] = stats.binom.pmf(groups[name]["x"], groups[name]["n"], p)
	max_name = names[0] if groups[names[0]]["pmf"] > groups[names[1]]["pmf"] else names[1]
	min_name = names[0] if groups[names[0]]["pmf"] < groups[names[1]]["pmf"] else names[1]
	likelihood_ratio = groups[max_name]["pmf"] / groups[min_name]["pmf"]

	return [max_name, min_name, likelihood_ratio]

def sampling_double_uneven(names, groups, p):
	"""
	Compute the likelihood ratio of the most likely group relative to the least likely group, while doubling the
	probabilities of uneven groups (e.g., "1_3_")
	"""
	for name in names:
		pmf = stats.binom.pmf(groups[name]["x"], groups[name]["n"], p)
		groups[name]["pmf"] = pmf if pmf == stats.binom.pmf(groups[name]["n"]/2, groups[name]["n"], p) else (pmf*2)
	max_name = names[0] if groups[names[0]]["pmf"] > groups[names[1]]["pmf"] else names[1]
	min_name = names[0] if groups[names[0]]["pmf"] < groups[names[1]]["pmf"] else names[1]
	likelihood_ratio = groups[max_name]["pmf"] / groups[min_name]["pmf"]

	return [max_name, min_name, likelihood_ratio]

def sampling_binom_test(names, groups, p):
	"""
	Compute the likelihood ratio of the most likely group relative to the least likely group, relative to their p-values
	computed from a two-tailed binomial test.
	"""
	for name in names:
		groups[name]["p-value"] = stats.binom_test(groups[name]["x"], groups[name]["n"], p, alternative="two-sided")
	max_name = names[0] if groups[names[0]]["p-value"] > groups[names[1]]["p-value"] else names[1]
	min_name = names[0] if groups[names[0]]["p-value"] < groups[names[1]]["p-value"] else names[1]
	likelihood_ratio = groups[max_name]["p-value"] / groups[min_name]["p-value"]

	return [max_name, min_name, likelihood_ratio]

if __name__ == "__main__":
	# Set up the experiment trials.
	trials = {
		"1": {"2_2_": {"x": 2, "n": 4}, "1_3_": {"x": 1, "n": 4}},
		"2": {"3_5_": {"x": 3, "n": 8}, "4_4_": {"x": 4, "n": 8}},
		"3": {"8_8_": {"x": 8, "n": 16}, "7_9_": {"x": 7, "n": 16}},
		"4": {"0_4_": {"x": 0, "n": 4}, "2_2_": {"x": 2, "n": 4}},
		"5": {"4_4_": {"x": 4, "n": 8}, "2_6_": {"x": 2, "n": 8}},
		"6": {"6_10_": {"x": 6, "n": 16}, "8_8_": {"x": 8, "n": 16}},
		"7": {"1_3_": {"x": 1, "n": 4}, "0_4_": {"x": 0, "n": 4}},
		"8": {"1_7_": {"x": 1, "n": 8}, "2_6_": {"x": 2, "n": 8}},
		"9": {"4_12_": {"x": 4, "n": 16}, "3_13_": {"x": 3, "n": 16}},
		"10": {"0_8_": {"x": 0, "n": 8}, "2_6_": {"x": 2, "n": 8}},
		"11": {"4_12_": {"x": 4, "n": 16}, "2_14_": {"x": 2, "n": 16}},
		"12": {"2_6_": {"x": 2, "n": 8}, "3_5_": {"x": 3, "n": 8}},
		"13": {"9_7_": {"x": 9, "n": 16}, "6_10_": {"x": 6, "n": 10}},
		"14": {"2_14_": {"x": 2, "n": 16}, "9_7_": {"x": 9, "n": 16}},
		"15": {"10_6_": {"x": 10, "n": 16}, "5_11_": {"x": 5, "n": 16}},
	}

	# Set up the ratio of blue-to-yellow balls in the container.
	p = 0.5

	# Compute and store the model predictions.
	with open("../data/model/model.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(["Trial", "Response", "PMF_Max_Name", "PMF_Min_Name", "PMF_Prediction", "DU_Max_Name", 
						 "DU_Min_Name", "DU_Prediction", "BT_Max_Name", "BT_Min_Name", "BT_Prediction"])
		for trial in trials:
			groups = trials[trial]
			names = list(groups.keys())
			[pmf_max_name, pmf_min_name, pmf_prediction] = sampling_pmf(names, groups, p)
			[du_max_name, du_min_name, du_prediction] = sampling_double_uneven(names, groups, p)
			[bt_max_name, bt_min_name, bt_prediction] = sampling_binom_test(names, groups, p)
			writer.writerow([trial, names[0], pmf_max_name, pmf_min_name, pmf_prediction, du_max_name, du_min_name, 
							 du_prediction, bt_max_name, bt_min_name, bt_prediction])
			writer.writerow([trial, names[1], pmf_max_name, pmf_min_name, (-pmf_prediction), du_max_name, du_min_name,
							 (-du_prediction), bt_max_name, bt_min_name, (-bt_prediction)])
