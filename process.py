import os
import sys
import argparse 

def chooseplatform():
    return sys.platform

# Constants and platform specific paths
# Change these accordingly!!
CEMRG = {
    'linux': r'$HOME/Desktop/CemrgApp-Linux-v2.2/CemrgApp-Linux'
}

SCAR_CMD = {
    'linux' : 'MitkCemrgScarProjectionOptions.sh',
}

CLIP_CMD = {
    'linux' : 'MitkCemrgApplyExternalClippers',
}

MIRTK = {
    'linux' : "$HOME/Desktop/CemrgApp-Linux-v2.2/CemrgApp-Linux/bin/MLib"
}

LOGFILE=''
def log_to_file(log_file, log_str, log_status='INFO') :
    """Write a string to a file"""
    with open(log_file, 'a') as f:
        f.write('[' + log_status + '] ' + log_str + '\n')

def fullfile(*args):
    """Join path components intelligently."""
    return os.path.join(*args)

def run_cmd(script_dir, cmd_name, arguments, debug = False ) :
    """ Return the command to execute""" 
    cmd_name = fullfile(script_dir, cmd_name) if script_dir != '' else cmd_name
    cmd = cmd_name + ' '
    cmd += ' '.join(arguments)
    stst = 0
    if LOGFILE != '' :
        log_to_file(LOGFILE, cmd)
    if debug:
        print(cmd)
    else :  
        stst = os.system(cmd)

    return stst, cmd 

def find_file_in_dir(dir, ext, contains_str, fallback_contains_str=None) :
    """Find a file in a directory"""
    forbidden = '._'
    res = None
    for f in os.listdir(dir) :
        if f.startswith(forbidden) :
            continue
        if f.endswith(ext) and contains_str in f : 
            res = f 
            break

    if res is None and fallback_contains_str is not None :
        res = find_file_in_dir(dir, ext, fallback_contains_str)
    
    return res


def get_folders(p2f: str):
    folders = os.listdir(p2f)
    folders.remove('options')
    return folders

def check_inputs(*some_args) :
    print('Checking inputs:') 
    for arg in some_args : 
        if arg is None : 
            raise ValueError(f'Input argument is None')
        else: 
            print(f'Input argument is {arg}')

    
def create_segmentation_mesh(dir: str, pveins_file='LA-reg.nii', iterations=1, isovalue = 0.5, blur=0.0, debug=False) : 
    arguments = [fullfile(dir, pveins_file)]
    arguments.append(fullfile(dir, 'segmentation.s.nii'))
    arguments.append('-iterations') 
    arguments.append(str(iterations))
    seg_1_out, _ = run_cmd(MIRTK[chooseplatform()], 'close-image', arguments, debug)
    
    if seg_1_out != 0: 
        print('Error in close image')
        log_to_file(LOGFILE, 'Error in close image')

    arguments.clear()
    arguments = [fullfile(dir, 'segmentation.s.nii')]
    arguments.append(fullfile(dir, 'segmentation.vtk'))
    arguments.append('-isovalue')
    arguments.append(str(isovalue))
    arguments.append('-blur')
    arguments.append(str(blur))
    seg_2_out, _ = run_cmd(MIRTK[chooseplatform()], 'extract-surface', arguments, debug)
    if seg_2_out != 0: 
        print('Error in extract surface')
       
    arguments.clear()
    arguments = [fullfile(dir, 'segmentation.vtk')]
    arguments.append(fullfile(dir, 'segmentation.vtk'))
    arguments.append('-iterations')
    arguments.append('10')
    seg_3_out, _ = run_cmd(MIRTK[chooseplatform()], 'smooth-surface', arguments, debug) 
    if seg_3_out != 0:
        print('Error in smooth surface')
      
    arguments.clear()

def scar_projection(dir: str, lge_file: str, measurements: int, sweep: str, debug=False):

    arguments = ['-i']
    arguments.append(fullfile(dir, lge_file))
    arguments.append('-m')
    arguments.append(str(measurements))
    arguments.append('-t')
    arguments.append(sweep)

    scar_out, _ = run_cmd(CEMRG[chooseplatform()], SCAR_CMD[chooseplatform()], arguments, debug)
    if scar_out != 0:
        print('Scar projection failed for ' + dir)

def main(args):
    """
    Functions: 
        + Create segmentation.vtk files
        + Get Scar Maps for each patient
        + Create comparisons of scar maps between pre and post
    """
    mode = args.mode
    debugging = args.debug
    base_dir = args.base_dir

    if mode == 'surf':
        iterations = args.surf_iterations
        isovalue = args.surf_isovalue
        blur = args.surf_blur

        check_inputs(base_dir, args.segmentation, iterations, isovalue, blur)
        create_segmentation_mesh(base_dir, args.segmentation, iterations, isovalue, blur, debug=debugging)
        
        if (args.segmentation != 'PVeinsCroppedImage') : 
            log_to_file(LOGFILE, f'Changing segmentation {args.segmentation} to PVeinsCroppedImage (for scar)')
            arguments = [fullfile(base_dir, args.segmentation), fullfile(base_dir, 'PVeinsCroppedImage.nii')]
            cp_out, _ = run_cmd('', 'cp', arguments, debug)
            if cp_out != 0:
                log_to_file('Conversion failed...')

    elif mode == 'scar':
        lge_file = args.scar_lge
        measurements = 1 if args.scar_measurements == 'iir' else 2
        sweep = args.scar_sweep

        check_inputs(base_dir, lge_file, measurements, sweep)
        scar_projection(base_dir, lge_file, measurements, sweep, debug=debugging)


if __name__ == '__main__':
    in_parser = argparse.ArgumentParser(description='SOME PROCESS.')
    in_parser.add_argument('mode', type=str, choices=['surf', 'scar'])
    in_parser.add_argument('-dir', '--base-dir', type=str, help='Base directory with data.', required=True) 
    in_parser.add_argument('-seg', '--segmentation', type=str, default='PVeinsCroppedImage.nii', required=False)
    in_parser.add_argument('-d', '--debug', action='store_true', help='Debugging mode')
    # parameters specific to surf mode
    in_parser.add_argument('--surf-iterations', type=int, default=1, required=False)
    in_parser.add_argument('--surf-isovalue', type=float, default=0.5, required=False)
    in_parser.add_argument('--surf-blur', type=float, default=0, required=False)
    # parameters specific to scar mode
    in_parser.add_argument('--scar-lge', type=str, required=False)
    in_parser.add_argument('--scar-measurements', type=str, choices=['iir', 'msd'], required=False)
    in_parser.add_argument('--scar-sweep', type=str, required=False)

    args = in_parser.parse_args()

    # date in format YYYYMMDD
    import datetime
    DATE = datetime.datetime.now().strftime('%Y%m%d')
    LOGFILE = os.path.join(args.base_dir, f'{args.mode}-{DATE}.log')
    log_to_file(LOGFILE, 'Starting...')

    main(args)
