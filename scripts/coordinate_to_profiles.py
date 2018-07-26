import os
import itertools
import subprocess
import multiprocessing

basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def coordinate_to_profiles(args):
    fname, Re = args
    if fname.endswith('.dat'): fname = fname[:-4]
    subpath = os.path.join(basepath, 'profiles', fname, str(Re))
    print(subpath)
    os.makedirs(subpath, exist_ok=True)
    fullname = os.path.join('coordinates', fname + '.dat')
    p = subprocess.Popen(['/usr/bin/xfoil', fullname],
                         cwd=subpath, stdin=subprocess.PIPE)
    p.stdin.write('oper\nvisc\n{}\n'.format(Re))
    for i in range(-5,9):
        p.stdin.write('alfa {}\n'.format(i))
        p.stdin.write('alfa.{}.txt\n'.format(i))
    p.stdin.write('\nquit\n')
    p.wait()

if __name__ == '__main__':
    files = os.listdir(os.path.join(basepath, 'coordinates'))
    Res = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000,
           500000, 1000000, 2000000, 5000000, 10000000, 20000000,
           50000000, 100000000, 200000000, 500000000, 1000000000]
    pool = multiprocessing.Pool()
    pool.map(coordinate_to_profiles, itertools.product(files, Res))
