import re

vocab_reverse = ['A',
                 'R',
                 'N',
                 'Nmod',
                 'D',
                 #~ 'C',
                 'Cmod',
                 'E',
                 'Q',
                 'Qmod',
                 'G',
                 'H',
                 'I',
                 'L',
                 'K',
                 'M',
                 'Mmod',
                 'F',
                 'P',
                 'S',
                 'T',
                 'W',
                 'Y',
                 'V',
                ]

mass_H = 1.0078
mass_H2O = 18.0106
mass_NH3 = 17.0265
mass_N_terminus = 1.0078
mass_C_terminus = 17.0027
mass_CO = 27.9949

mass_AA = {'_PAD': 0.0,
           '_GO': mass_N_terminus-mass_H,
           '_EOS': mass_C_terminus+mass_H,
           'A': 71.03711, # 0
           'R': 156.10111, # 1
           'N': 114.04293, # 2
           'Nmod': 115.02695,
           'D': 115.02694, # 3
           #~ 'C': 103.00919, # 4
           'Cmod': 160.03065, # C(+57.02)
           #~ 'Cmod': 161.01919, # C(+58.01) # orbi
           'E': 129.04259, # 5
           'Q': 128.05858, # 6
           'Qmod': 129.0426,
           'G': 57.02146, # 7
           'H': 137.05891, # 8
           'I': 113.08406, # 9
           'L': 113.08406, # 10
           'K': 128.09496, # 11
           'M': 131.04049, # 12
           'Mmod': 147.0354,
           'F': 147.06841, # 13
           'P': 97.05276, # 14
           'S': 87.03203, # 15
           'T': 101.04768, # 16
           'W': 186.07931, # 17
           'Y': 163.06333, # 18
           'V': 99.06841, # 19
          }

MAX_LEN = 30
MZ_MAX = 3000.0
PRECURSOR_MASS_PRECISION_INPUT_FILTER = 100


def inspect_mgf_location(input_file):
	print("inspect_mgf_location(), input_file = ", input_file)
	keyword = "BEGIN IONS"
	spectra_file_location = []
	with open(input_file, mode="r") as file_handle:
		line = True
		while line:
			file_location = file_handle.tell()
			line = file_handle.readline()
			if keyword in line:
				spectra_file_location.append(file_location)
	print('find # spectra_locations:', len(spectra_file_location))
	return spectra_file_location


def read_mgf(input_file):
	spectra_locations = inspect_mgf_location(input_file)
	file_handle = open(input_file, mode="r")
	data_set = []

	counter = 0
	counter_skipped = 0
	counter_skipped_mod = 0
	counter_skipped_aa = 0
	counter_skipped_len = 0
	counter_skipped_mass = 0
	counter_skipped_mass_precision = 0
	avg_peak_count = 0.0
	avg_peptide_len = 0.0

	keyword = "BEGIN IONS"

	for location in spectra_locations:
		file_handle.seek(location)
		line = file_handle.readline()
		assert (keyword in line), "ERROR: read_spectra(); wrong format"

		unknown_modification = False
		unknown_AA = False

		# header TITLE
		line = file_handle.readline()

		# header PEPMASS
		line = file_handle.readline()
		peptide_ion_mz = float(re.split('=|\n', line)[1])

		# header CHARGE
		line = file_handle.readline()
		charge = float(re.split('=|\+', line)[1])

		# compute peptide_mass
		peptide_mass = peptide_ion_mz*charge - charge*mass_H

		# header SCANS
		line = file_handle.readline()
		scan = re.split('=|\n', line)[1]

		scan_number = scan.split(':')[1]

		# header RTINSECONDS
		line = file_handle.readline()

		# header SEQ
		line = file_handle.readline()
		raw_sequence = re.split('=|\n|\r', line)[1]
		
		###########################
		## for unknown sequences ##
		if raw_sequence == 'UNKNOWN':
			peptide = ['A' for i in range(20)]
		else:
			raw_sequence_len = len(raw_sequence)

			peptide = []
			index = 0
			while index < raw_sequence_len:
				if raw_sequence[index] == "(":
					if peptide[-1] == "C" and raw_sequence[index:index+8] == "(+57.02)":
						peptide[-1] = "Cmod"
						index += 8
					elif peptide[-1] == 'M' and raw_sequence[index:index+8] == "(+15.99)":
						peptide[-1] = 'Mmod'
						index += 8
					elif peptide[-1] == 'N' and raw_sequence[index:index+6] == "(+.98)":
						peptide[-1] = 'Nmod'
						index += 6
					elif peptide[-1] == 'Q' and raw_sequence[index:index+6] == "(+.98)":
						peptide[-1] = 'Qmod'
						index += 6
					else: # unknown modification					
						unknown_modification = True
						break
				elif raw_sequence[index] not in vocab_reverse:
					unknown_AA = True
					break
				else:
					peptide.append(raw_sequence[index])
					index += 1
		## for unknown sequences ##
		###########################

		# skip if unknown_modification
		if unknown_modification:
			counter_skipped += 1
			counter_skipped_mod += 1
			continue

		# skip if unknown_modification
		if unknown_AA:
			counter_skipped += 1
			counter_skipped_aa += 1
			continue

		# skip if neutral peptide_mass > MZ_MAX(3000.0)
		if peptide_mass > MZ_MAX:
			counter_skipped += 1
			counter_skipped_mass += 1
			continue

		# TRAINING-SKIP: skip if peptide length > MAX_LEN(30)
		# TESTING-ERROR: not allow peptide length > MAX_LEN(50)
		peptide_len = len(peptide)
		if peptide_len > MAX_LEN:
			counter_skipped += 1
			counter_skipped_len += 1
			continue

		# DEPRECATED-TRAINING-ONLY: testing peptide_mass & sequence_mass
		if raw_sequence == 'UNKNOWN':
			pass
		else:
			sequence_mass = sum(mass_AA[aa] for aa in peptide)
			sequence_mass += mass_N_terminus + mass_C_terminus
			if (abs(peptide_mass-sequence_mass)
					> PRECURSOR_MASS_PRECISION_INPUT_FILTER):
				counter_skipped_mass_precision += 1
				counter_skipped += 1
				continue

		# read spectrum
		spectrum_mz = []
		spectrum_intensity = []
		line = file_handle.readline()
		while not "END IONS" in line:
			# parse pairs of "mz intensity"
			mz, intensity = re.split(' |\n', line)[:2]
			intensity_float = float(intensity)
			mz_float = float(mz)
			if mz_float > MZ_MAX: # skip this peak
				line = file_handle.readline()
				continue
			spectrum_mz.append(mz_float)
			spectrum_intensity.append(intensity_float)
			line = file_handle.readline()

		data_set.append((scan_number, peptide_mass, spectrum_mz, spectrum_intensity, peptide))
	
		# AN ENTRY FOUND
		counter += 1
		if counter % 10000 == 0:
			print("  reading peptide %d" % counter)

		# Average number of peaks per spectrum
		peak_count = len(spectrum_mz)
		avg_peak_count += peak_count

		# Average peptide length
		avg_peptide_len += peptide_len

	print("  total peptide read %d" % counter)
	print("  total peptide skipped %d" % counter_skipped)
	print("  total peptide skipped by mod %d" % counter_skipped_mod)
	print("  total peptide skipped by unknown AA %d" % counter_skipped_aa)
	print("  total peptide skipped by len %d" % counter_skipped_len)
	print("  total peptide skipped by mass %d" % counter_skipped_mass)
	print("  total peptide skipped by mass precision %d"
				% counter_skipped_mass_precision)

	print("  average #peaks per spectrum %.1f" % (avg_peak_count/counter))
	print("  average peptide length %.1f" % (avg_peptide_len/counter))

	return data_set