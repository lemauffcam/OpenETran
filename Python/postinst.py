import sys
import os.path as osp
import subprocess

guiExecutable = osp.join(sys.prefix, "Scripts", "openetran_py3.exe")
cfoadded_path = osp.join(sys.prefix, "Lib", "site-packages","openetran_py3","win","CFO_Added.xlsm")
internet_path = "http://openetran.readthedocs.io/"

working_dir = osp.join(sys.prefix, "Lib", "site-packages","openetran_py3","win")

pippath = osp.join(sys.prefix, "Scripts", "pip.exe")

if sys.argv[1] == '-install':
    # Get paths to the desktop
    desktop_path = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")

    # Create shortcuts.
    for path in [desktop_path, startmenu_path]:
        create_shortcut(guiExecutable,
						"OpenEtran_GUI",
						osp.join(path,"openetran_py3.lnk"),
						working_dir)

        create_shortcut(cfoadded_path,
						"CFO_Added Tool",
						osp.join(path,"CFO_Added.lnk"),
						working_dir)

        create_shortcut(internet_path,
                        "Documentation",
                        osp.join(path,"docs.lnk"),
                        working_dir)

	# Call pip to install matplotlib and PyQt
    args=[pippath, 'install', 'matplotlib==2.0.2']
    subprocess.run(args,stdout=subprocess.PIPE)

    args=[pippath, 'install', 'PyQt5']
    subprocess.run(args,stdout=subprocess.PIPE)