import os
import subprocess

basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def coordinate_to_profiles(fname, Re):
    fullname = os.path.join('coordinates', fname + '.dat')
    print(os.path.abspath(fullname))
    p = subprocess.Popen(['/usr/bin/xfoil', fullname],
                         cwd=basepath, stdin=subprocess.PIPE)
    p.stdin.write('oper\nvisc\n{}\n'.format(Re))
    for i in range(-5,9):
        p.stdin.write('alfa {}\n'.format(i))
        dumpname = os.path.join('profiles', fname)
        p.stdin.write('dump {}.Re{}.alfa{}\n'.format(dumpname, Re, i))
    p.stdin.write('\nquit\n')
    p.wait()

if __name__ == '__main__':
    coordinate_to_invscid('goe500', 1000)
