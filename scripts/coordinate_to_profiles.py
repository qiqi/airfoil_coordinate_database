import os
import sys
import time
import itertools
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
    fullname = os.path.join('../../../coordinates', fname + '.dat')
    print(os.path.abspath(subpath))
    with open(os.path.join(subpath, 'xfoil.stdout'), 'wt') as f:
        p = subprocess.Popen(['/usr/bin/xfoil', fullname],
                             cwd=subpath, stdin=subprocess.PIPE)
        try:
            p.stdin.write('oper\nvisc\n{}\n'.format(Re))
            for i in range(-5,-5):
                p.stdin.write('alfa {}\n!\n'.format(i))
                p.stdin.write('dump alfa.{}.txt\n'.format(i))
            p.stdin.write('\n\nquit\n')
            p.stdin.flush()
            for i in range(100):
                if p.poll() is not None:
                    return
                p.stdin.write('\n\nquit\n')
                p.stdin.flush()
                time.sleep(0.1)
        except:
            pass
        p.kill()

if __name__ == '__main__':
    files = sorted(os.listdir(os.path.join(basepath, 'coordinates')))
    Res = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000,
           500000, 1000000, 2000000, 5000000, 10000000, 20000000,
           50000000, 100000000, 200000000, 500000000, 1000000000]
    pool = multiprocessing.Pool()
    pool.map(coordinate_to_profiles, itertools.product(files, Res))
