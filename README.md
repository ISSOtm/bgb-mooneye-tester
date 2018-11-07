# bgb-mooneye-tester
A Python script that automatically runs mooneye-gb's tests on BGB.

# Requirements
- [BGB](http://bgb.bircd.org); versions too old might not support the command-line options used
- Python 3. Normally all the libs used should be included by default, but if not, all import directives are in the first few lines of the script
- [mooneye-gb](https://github.com/Gekkio/mooneye-gb)'s test ROMs. You can either compile them yourself, or use the link in the README to grab them pre-compiled.

# Running
First, get the Python script and INI file, and place them at the root of the folder where the ROMs are located. (The files should be alongside the `acceptance`, `emulator-only` etc. folders.) You should delete the `utils` folder.

Then, create a `boot_roms` folder in BGB's folder, and inside, put the boot ROM that matches each system (`dmg0.bin`, `dmg.bin`, `mgb.bin`, `sgb.bin`, `sgb2.bin`, `cgb0.bin`, `cgb.bin`, `agb.bin`, `ags.bin`). (**Note: this doesn't seem to do anything, but running the DMG0 tests manually confirms that they work.**)

Then, run `run_bgb_tests.py bgb_cmd`, where `bgb_cmd` is the command used to launch BGB. Then wait until all tests are run.

## Output
A temporary file `out.state` will be created during the tests. This file is not needed after completion of all tests, and can be safely deleted.

A recap of all results will be produced in `results.txt`. If an error occurred, the file's contents should be preserved. This file lists completion of each test for each console model and/or revision that it ran on. (Some tests don't work on all models/revisions.)
- **Pass** signifies that the test was successful
- **Fail** signifies that the test completed, but failed. Note that the `manual-only/sprite_priority` ROM will be auto-detected as a "Fail", but that's because it doesn't work in an automated way. You need to manually compare it against the [reference image](https://github.com/Gekkio/mooneye-gb/blob/master/tests/manual-only/sprite_priority-expected.png).
- **Hang@0x????** signifies that the test wasn't detected as completed after 80 seconds (roughly) of emulated time, and that after this delay, PC was at 0x????. Detection should be fairly robust, but might still fail.

Screenshots of completion (or hang) screens will be produced, but may require a bit of setup. If BGB is in the same folder as the `run_bgb_tests.py` script, everything will work automatically; otherwise, after running the tests once, copy or move the `screenshots` folder in BGB's folder. Subsequent testing sessions will generate the screenshots in the `screenshots` folder (this is a limitation of how BGB currently works, and might change in the future.)


# TODO

- Multithreadify this. It's REALLY slow.
- Also run [Wilbert Pol's tests](https://github.com/wilbertpol/mooneye-gb)
