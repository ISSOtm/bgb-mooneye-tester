#!/usr/bin/python3

import os
from sys import argv
from pathlib import Path
import re


assert len(argv) >= 2, "Usage: {} bgb_command".format(argv[0])

systems_codes = {
	"all":  ["dmg0", "dmg", "mgb", "sgb", "sgb2", "cgb0", "cgb", "agb", "ags"],

	"G":    ["dmg0", "dmg", "mgb"],
	"S":    ["sgb", "sgb2"],
	"C":    ["cgb0", "cgb", "agb", "ags"],
	"A":    ["agb", "ags"],

	"dmg0": ["dmg0"],
	"dmg":  ["dmg"],
	"mgb":  ["mgb"],
	"sgb":  ["sgb"],
	"sgb2": ["sgb2"],
	"cgb0": ["cgb0"],
	"cgb":  ["cgb"],
	"agb":  ["agb"],
	"ags":  ["ags"]
}

systems_settings = {
	"dmg0": {"SystemMode": 0, "DetectGBP": 0, "DetectGBA": 0},
	"dmg":  {"SystemMode": 0, "DetectGBP": 0, "DetectGBA": 0},
	"mgb":  {"SystemMode": 0, "DetectGBP": 1, "DetectGBA": 0},
	"sgb":  {"SystemMode": 2, "DetectGBP": 0, "DetectGBA": 0},
	"sgb2": {"SystemMode": 2, "DetectGBP": 1, "DetectGBA": 0},
	"cgb0": {"SystemMode": 1, "DetectGBP": 0, "DetectGBA": 0},
	"cgb":  {"SystemMode": 1, "DetectGBP": 0, "DetectGBA": 0},
	"agb":  {"SystemMode": 1, "DetectGBP": 0, "DetectGBA": 1},
	"ags":  {"SystemMode": 1, "DetectGBP": 0, "DetectGBA": 1}
}
rom_from_mode = ["DmgBootRom", "CgbBootRom", "SgbBootRom"]

system_regex = re.compile('(G|S|C|A|dmg0?A?B?C?|mgb|sgb2?|cgb0?A?B?C?D?E?|agb0?A?B?|ags0?A?B?)')
revs_regex   = re.compile('[ABCDE]')


# Generate setting list
settings = []
with open("bgb.ini", "rt") as ini_file:
	for line in ini_file:
		settings.append('-set "{}"'.format(line.replace('\n', '')))

# Process all ROMs
rom_list = list(Path('.').rglob('*.gb'))
results = {}
rom_i = 0
for rom_path in rom_list:
	rom_i += 1
	print("Running test {} ({}/{})".format(rom_path.as_posix(), rom_i, len(rom_list)))

	# Customize which system(s) should be used depending on the ROM name
	rom_name = rom_path.stem
	if rom_name.count('-') == 0:
		# Works on all systems
		systems = systems_codes["all"]
	else:
		# Only works on a precise system
		index = rom_name.rindex('-')
		systems = []
		for code in system_regex.findall(rom_name[index+1:]):
			if code[0].islower():
				code = revs_regex.sub('', code)
			systems.extend(systems_codes[code])

	system_results = {}
	system_i = 0
	for system in systems:
		system_i += 1
		print("System: {} ({}/{})".format(system, system_i, len(systems)), end=' => ')
		# Pick settings based on model
		# Corresponding settings are SystemMode, DetectGBP, and DetectGBA
		# And also the corresponding boot ROM
		system_settings = ["-set {}={}".format(*pair) for pair in list(systems_settings[system].items()) + [(rom_from_mode[systems_settings[system]["SystemMode"]], "boot-roms/{}.bin".format(system))]]

		screenshot_name = 'screenshots/' + rom_path.as_posix().replace('.gb', '__{}.bmp'.format(system))
		# Create the directories the file will be in
		Path(screenshot_name).parent.mkdir(parents=True, exist_ok=True)
		# Run BGB
		command = '{} -hf -rom {} -br "/TOTALCLKS>=9896800/" {} -stateonexit out.state -screenonexit {}'.format(argv[1], rom_path, " ".join(settings + system_settings), screenshot_name)
		os.system(command)

		rom_results = {}
		required_props = ["AF", "BC", "DE", "HL", "PC", "WRAM", "HRAM"]
		with open("out.state", "rb") as out_file:
			# Parse BGB's save state file
			# Format: name (zero-terminated), length (4 bytes LE), data (for registers, it's LE)
			while required_props:
				# Read name
				name = []
				while True:
					byte = out_file.read(1)[0]
					if byte == 0:
						break
					name.append(byte)
				name = bytes(name).decode('ascii')
				# Read length
				length = int.from_bytes(out_file.read(4), "little")
				# Read value
				value = out_file.read(length)

				# Check if name corresponds to anything we're looking for
				if name in required_props:
					required_props.remove(name)
					rom_results[name] = value

			# Check if test succeeded
			bc = int.from_bytes(rom_results["BC"], "little")
			de = int.from_bytes(rom_results["DE"], "little")
			hl = int.from_bytes(rom_results["HL"], "little")
			pc = int.from_bytes(rom_results["PC"], "little")
			if pc < 0x8000:
				with open(rom_path, "rb") as rom_file:
					rom_file.seek(pc) # Assuming the loaded bank is 1..!
					op = int.from_bytes(rom_file.read(1), "little")
			elif pc < 0xE000:
				assert pc >= 0xC000, "I never expected a test to end in VRAM: " + hex(pc)
				op = rom_results["WRAM"][pc - 0xC000]
			else:
				assert pc >= 0xFF80, "I never expected a test to end in EX/FXXX: " + hex(pc)
				op = rom_results["HRAM"][pc - 0xFF80]
				
		if op != 0x40: # ld b, b
			system_results[system] = "Hang@" + hex(pc)
		elif bc == 0x0305 and de == 0x080D and hl == 0x1522:
			system_results[system] = "Pass"
		else:
			system_results[system] = "Fail"
		print(system_results[system])

	results[rom_path.as_posix()] = system_results

with open("results.txt", "wt") as results_file:
	for name,result in results.items():
		print("{}: {}".format(name, ", ".join(["{} = {}".format(system, status) for system,status in result.items()])), file=results_file)

