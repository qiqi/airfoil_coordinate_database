import os
import sys
import time
import itertools
import traceback
import subprocess
import multiprocessing

basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def completed(subpath):
    for i in range(-5,9):
        fname = os.path.join(subpath, 'alfa.{}.txt'.format(i))
        if not os.path.exists(fname):
            return False
    return True

def coordinate_to_profiles(args):
    fname, Re = args
    if fname.endswith('.dat'): fname = fname[:-4]
    subpath = os.path.join(basepath, 'profiles', fname, str(Re))
    if completed(subpath): return
    if not os.path.exists(subpath): os.makedirs(subpath)
    fullname = os.path.join(basepath, 'coordinates', fname + '.dat')
    if not os.path.exists(os.path.join(subpath, fname)):
        os.link(fullname, os.path.join(subpath, fname))
    print(os.path.abspath(subpath))
    with open(os.path.join(subpath, 'xfoil.stdout'), 'wt') as f:
        p = subprocess.Popen(['/usr/bin/xfoil', fname],
                             cwd=subpath, stdin=subprocess.PIPE,
                             stdout=f, stderr=f)
        try:
            p.stdin.write('oper\nvisc\n{}\n'.format(Re).encode())
            for i in range(-5,9):
                p.stdin.write('alfa {}\n!\n'.format(i).encode())
                p.stdin.write('dump alfa.{}.txt\n'.format(i).encode())
            p.stdin.write('\n\nquit\n'.encode())
            p.stdin.flush()
            for i in range(100):
                if p.poll() is not None:
                    return
                p.stdin.write('\n\nquit\n'.encode())
                p.stdin.flush()
                time.sleep(0.1)
        except:
            _,_,tb = sys.exe_info()
            traceback.print_tb(tb)
        p.kill()

if __name__ == '__main__':
    files = sorted(os.listdir(os.path.join(basepath, 'coordinates')))
    Res = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000,
           500000, 1000000, 2000000, 5000000, 10000000, 20000000,
           50000000, 100000000, 200000000, 500000000, 1000000000]
    pool = multiprocessing.Pool()
    pool.map(coordinate_to_profiles, itertools.product(files, Res))
