# **BareDroid** #

This project wants to introduce a new malware analysis framework...

## Folders ##

**backup**: used to create a backup of the device. It is a bash script which stores a copy of:
* userdata
* system
* boot 
in the *store* partition (partition number 30). This is needed only when you want to setup a new device.

**restore**: used to restore a previous backup. It is a bash script which restore a) system, b) userdata and c) userdatanew partition.

**backup_and_restore**: used to create a backup and restore it. It is a merge of the previous scripts.

**setup_device**: contains images, libraries and apks used to setup a device. More specifically:
*	openrecovery-twrp-2.8.1.0-hammerhead.img: recovery image;
*	pa_gapps-modular-full-4.4.4-20141011-signed.zip: gapps;
*	UPDATE-SuperSU-v2.16.apk: SuperSU library;
*	de.robv.android.xposed.installer_v32_de4f0d.apk: Xposed framework;
*	xposed.apk: Bill's module;
*	script: used to setup a device. Basically, this script creates the new partitions;
*	push.sh: used to push the files, such as copy (used by the infrastructure to update the device) and loggedfs (used to get info about FUSE file system) on the device.

---

**update**: contains the python scripts used to manage the infrastructure.
*	adb.py: provides APIs used to send command through adb shell;
*	device.py: contains information about the update_manager associated to the device (deprecated, not used in the next version);
*	analysis.py: it bridges the gap between the infrastructure and the experiments. For a detailed description see below;
*	util.py: provides utilities (deprecated);
*	manager.py: manages the command line interface;
*	updtae_manager.py: it is the core of the infrastructure. It is a separate process which manages the update and analysis process;
*	update_manager_device.py: represents a separate process used to update the device during the analysis;
*	update_manager_recovery.py: represents a separate process used to update the device during the reboot. it is used to perform a relabel of the userdata partition ( SELinux :) );

**update/config**: contains cfg and info files used to setup the python scripts.
*	config.cfg: contains the information about where to save the logs, and which scripts use to perform the analysis (e.g., ransomware scripts)
*	devices.info: contains general information about the devices (e.g., user, AndroidId)

## How to backup ##
1.	connect the device
2.	run the "./script" file (the script reboots the device in recovery mode and run the script)
3.	reboot the device


## How to restore ##
1. connect the device
2. run the "./script" file (the script reboots the device in recovery mode and run the script)
3. reboot the device


## Analysis script ##
The goal of this script is to provide a wrapper between the experiment and the infrastructure, *SetupAndStart* is the main method and the only one called by the infrastructure (i.e., update_manager.py line 178). It setups the environment for the experiment (e.g., adb root) and run the experiment.
If you want to use your code in an experiment you need to:
1.	modify the config.cfg file. In the stanza 'Project' as folder put the absolute path to the code that you want to use;
2.	create an experiment.py file containing the 'Experiment' class (in the next version I will use a different approach for noe this works fine...);
3.	define a 'run' method in the Experiment class. This is the method used by the wrapper to start the experiment; 

In the next version I will use only the *config.cfg* file in order to have a clear distinction between the experiment and the infrastructure...

## how to add a new device to the infrastructure ##

1.	see 'setup_device';
2.	run the backup and restore scripts;
3.	add info to the 'update/config/device.info' file (e.g., AndroidId); [mandatory]

general consideration:

4.	device -> Settings -> Storage -> USB computer connection -> disable  MTP
5.	device -> Security -> Screen lock -> None
6.	be sure you can install untrusted app (i.e., from outside the market)


## How to run an experiment ##
*I will use the Bill's script as example*

Architectural overview:

![alt tag](https://docs.google.com/drawings/d/1UXaQkFElMduaZckbcicz3zloDz9SOA5aap_CV0FFMhQ/pub?w=465&amp;h=259)


1.	to run an experiment you need to include the absolute path of the experiment folder in the *update/config/config.cfg* file:

example

```
  ...
  [Project]
  folder=/home/mutti/git/ransomware/experimental/
```
2.	run the manager script against the folder (specified using the 'd' option) containing the apps to analyze;

example

```
python manager.py -d path/to/folder/
```

3.	the script will prompt a command line interface which allows the user to interact with the infrastructure (e.g., start experiment);
4.	select option '2' to run the experiment;
5.	when the experiment is finished click on 'q'; (due to uiautomator problem run *killall python* :) )
6.	the results are stored in the 'update/experiment' folder.



---

*author:* Simone Mutti
*email:* simone.mutti@unibg.it
