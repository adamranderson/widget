import subprocess, os, sys, shutil

#Checks to see if f exists as a directory
#Creates it if not
def ensure_dir(f):
    d = f
    if not os.path.exists(d):
        os.makedirs(d)

#Parses the command line arguments
#Returns them as a dictionary
def parse_commandline_args():
    settings = {
        "input_file" : "input.xml",
        "output_file" : "output.xml",
        "results_dir" : "results",
        "verbose" : False,
        "help" : False,
        "remote" : False,
        "remote-configs" : None,
        "use-joval" : False
        }
    for i in range(len(sys.argv)):
        arg = sys.argv[i]
        if arg == "-i":
            i += 1
            settings['input_file'] = sys.argv[i]
        elif arg == "-o":
            i += 1
            settings['output_file'] = sys.argv[i]
        elif arg == "-d":
            i += 1
            settings['results_dir'] = sys.argv[i]
        elif arg == "-v":
            settings['verbose'] = True
        elif arg == "-h" or arg == "--h" or arg == "--help":
            settings['help'] = True
        elif arg == "-remote":
            settings['remote'] = True
            settings['user-joval'] = True
        elif arg == "-configs":
            i += 1
            settings['remote-configs'] = sys.argv[i]
        elif arg == "-joval":
            settings['use-joval'] = True
    return settings

#Prints out how to use this script
def helpme():
    print "Arguments:"
    tab = " "*2
    print tab + "%s : %s" % ("-i path", "Path to the input file (Anubis)")
    print tab + "%s : %s" % ("-o path", "Path to the output file")
    print tab + "%s : %s" % ("-d path", "Path to the results directory")
    print tab + "%s : %s" % ("-configs path", "Path to the remote configs directory")
    print tab + "%s : %s" % ("-remote", "Turns on remote scanning.  Will also need -configs")
    print tab + "%s : %s" % ("-joval", "Use joval for scanning localhost instead of ovaldi")
    print tab + "%s : %s" % ("-v", "Verbose")
    sys.exit()

#Prints out the settings being used by the script
def print_settings(settings):
    verboseprint("Settings:")
    for (key, val) in settings.iteritems():
        verboseprint("%s%s = %s" % (" "*2, key, val))

settings = parse_commandline_args()
#Define verbose
if settings['verbose']:
    def verboseprint(*args):
        # Print each argument separately so caller doesn't need to
        # stuff everything to be printed into a single string
        for arg in args:
           print arg,
        print
else:   
    verboseprint = lambda *a: None      # do-nothing function

print_settings(settings)
if settings['help']:
    helpme()
ensure_dir(settings['results_dir'])
anubis_to_maec = "\"Scripts/anubis_to_maec/0.92 (MAEC 2.1)/anubis_to_maec.py\""
maec_to_oval = '"Scripts/maec_to_oval/0.92 (MAEC 2.1)/maec_to_oval.py"'
oval_dir = "ovaldi"
oval_executable = "ovaldi.exe"
ovaldi = os.path.join(oval_dir, oval_executable)
joval_dir = "jOVAL"
joval_executable = "jovaldi.sh"
jovaldi = os.path.join(joval_dir, joval_executable)
stage = settings['results_dir']
anubis_file = settings['input_file']
maec_file = "maec.xml"
maec_path = os.path.join(stage, maec_file)
oval_file = "oval.xml"
oval_path = os.path.join(stage, oval_file)
results_file = "results.xml"
results_path = os.path.join(stage, results_file)
output_path = settings['output_file']

#Copy the input file to the results directory
input_filename = os.path.basename(anubis_file)
shutil.copyfile(anubis_file, os.path.join(stage, "anubis.xml"))

#Convert anubis to maec
cmd = "python %s -i %s -o %s" % (anubis_to_maec, anubis_file, maec_path)
verboseprint("Converting anubis to maec")
verboseprint("Running "+cmd)
output = subprocess.check_output(cmd, shell=True)
verboseprint(output)


#Convert maec to oval
cmd = "python %s -i %s -o %s" % (maec_to_oval, maec_path, oval_path)
verboseprint("Converting maec to oval")
verboseprint("Running "+cmd)
output = subprocess.check_output(cmd, shell=True)
verboseprint(output)


#function for running a remote scan
def joval_remote_scan(joval_dir, joval_executable, oval_path, config_path, results_path):
    cwd = joval_dir
    cmd = 'sh %s -m -o "%s" -d "%s" -plugin remote -config "%s"' % (joval_executable, os.path.abspath(oval_path), 
                            os.path.abspath(results_path), os.path.abspath(config_path))
    verboseprint("Running remote jOVAL scan %s" % (config_path))
    verboseprint("Running "+cmd)
    output = subprocess.check_output(cmd, shell=True, cwd=cwd)
    verboseprint(output)

    #copy the results file to the file the user wants
    #shutil.copyfile(results_path, output_path)


if settings['remote']:
    ensure_dir(output_path)
    remote_configs = os.listdir(settings['remote-configs'])
    for remote_config in remote_configs:
        if remote_config.endswith(".properties"):
            remote_config_path = os.path.join(settings['remote-configs'], remote_config)
            remote_results_filename = os.path.splitext(remote_config)[0]+"_results.xml"
            stage_results = os.path.join(stage, remote_results_filename)
            joval_remote_scan(joval_dir, joval_executable, oval_path, remote_config_path, stage_results)
            shutil.copyfile(stage_results, os.path.join(output_path, remote_results_filename))
    verboseprint("Results saved to "+output_path)
else:
    if settings['use-joval']:
        cwd = joval_dir
        cmd = 'sh %s -m -o "%s" -d "%s"' % (joval_executable, os.path.abspath(oval_path), os.path.abspath(results_path))
        verboseprint("Running jOVAL scan")
        verboseprint("Running "+cmd)
        output = subprocess.check_output(cmd, shell=True, cwd=cwd)
        verboseprint(output)

        #copy the results file to the file the user wants
        shutil.copyfile(results_path, output_path)
    else:
        #Run oval and get results
        cwd = oval_dir
        cmd = '%s -m -o "%s" -d "%s"' % (joval_executable, os.path.abspath(oval_path), os.path.abspath(results_path))
        verboseprint("Running oval scan")
        verboseprint("Running "+cmd)
        output = subprocess.check_output(cmd, shell=True, cwd=cwd)
        verboseprint(output)

        #copy the results file to the file the user wants
        shutil.copyfile(results_path, output_path)
    
