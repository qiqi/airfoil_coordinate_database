import os
import itertools
import multiprocessing
from numpy import *
import scipy.interpolate

basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def extract_transition_from_output(fname):
    x1, x2 = 1, 1
    for line in open(fname):
        if line.strip().startswith('Side 1') and ' transition ' in line:
            x1 = float(line.split()[-2])
        if line.strip().startswith('Side 2') and ' transition ' in line:
            x2 = float(line.split()[-2])
    return x1, x2

def extract_profile_from_output(fname, x1, x2):
    with open(fname) as f:
        header = f.readline()
        assert header.startswith('#')
        while True:
            line = f.readline()
            x = float(line[10:19])
            if x < x1 or x > 1:
                break
        s, Ue, Dstar, Theta = [], [], [], []
        xLast = x
        while x <= xLast or x < x2:
            if '*' not in line[:57]:
                s.append(float(line[1:10]))
                Ue.append(float(line[28:37]))
                Dstar.append(float(line[37:47]))
                Theta.append(float(line[47:57]))
            line = f.readline()
            xLast = x
            x = float(line[10:19])
    if len(s) > 3:
        sInterp = linspace(s[0], s[-1], 501)
        Ue = scipy.interpolate.interp1d(array(s), array(Ue), 'cubic')
        Dstar = scipy.interpolate.interp1d(array(s), array(Dstar), 'cubic')
        Theta = scipy.interpolate.interp1d(array(s), array(Theta), 'cubic')
        return sInterp, Ue(sInterp), Dstar(sInterp), Theta(sInterp)

def extract_profile_from_dir(dirname):
    for alpha in range(-4, 9):
        fname = os.path.join(dirname, 'xfoil.{}.stdout'.format(alpha))
        x1, x2 = extract_transition_from_output(fname)
        fname = os.path.join(dirname, 'alfa.{}.txt'.format(alpha))
        data = extract_profile_from_output(fname, x1, x2)
        if data:
            save(os.path.join(dirname, 'laminar.{}.npy'.format(alpha)), data)

def extract_profile(args):
    fname, Re = args
    if fname.endswith('.dat'): fname = fname[:-4]
    subpath = os.path.join(basepath, 'profiles', fname, str(Re))
    extract_profile_from_dir(subpath)

if __name__ == '__main__':
    files = sorted(os.listdir(os.path.join(basepath, 'coordinates')))
    Res = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000,
           500000, 1000000, 2000000, 5000000, 10000000, 20000000,
           50000000, 100000000, 200000000, 500000000, 1000000000]
    pool = multiprocessing.Pool()
    pool.map(extract_profile, itertools.product(files[:1], Res))
