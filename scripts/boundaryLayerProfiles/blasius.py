import sys
from pylab import *
from numpy import *
from scipy.integrate import odeint
from scipy.interpolate import interp1d

def odefun(F, eta):
    f1, f2, f3, f1p, f2p, f3p = F.T
    return hstack([f2,  f3,  -0.5 * f1 * f3,
                   f2p, f3p, -0.5 * (f1 * f3p + f1p * f3)])

class Blasius:
    def __init__(self, tol=1E-8, etaMax=8, numEta=801):
        self.eta = np.linspace(0, etaMax, numEta)
        f3init = 0.4696
        for i in range(10):
            F = odeint(odefun, [0,0,f3init,0,0,1], self.eta)
            mismatch = 1 - F[-1,1]
            if abs(mismatch) < tol:
                break
            f3init += mismatch / F[-1,4]

        if abs(mismatch) >= tol:
            print('Failed to reach tolerance of {}. Final mismatch: {}'.format(
                  tol, abs(mismatch)), file=sys.stderr)

        self.F1 = interp1d(self.eta, F[:,0], kind='cubic', assume_sorted=True)
        self.F2 = interp1d(self.eta, F[:,1], kind='cubic', assume_sorted=True)
        self.F3 = interp1d(self.eta, F[:,2], kind='cubic', assume_sorted=True)

    def U(self, eta):
        eta = array(eta, float)
        assert (eta >= 0).all()
        res = empty_like(eta)
        res[eta <= self.eta[-1]] = self.F2(eta[eta <= self.eta[-1]])
        res[eta > self.eta[-1]] = 1
        return res

    def Uint(self, eta):
        eta = array(eta, float)
        assert (eta >= 0).all()
        res = empty_like(eta)
        res[eta <= self.eta[-1]] = self.F1(eta[eta <= self.eta[-1]])
        res[eta > self.eta[-1]] = eta[eta > self.eta[-1]] \
                                + self.F1(self.eta[-1]) - self.eta[-1]
        return res

    def dUdy(self, eta):
        eta = array(eta, float)
        assert (eta >= 0).all()
        res = zeros_like(eta)
        res[eta <= self.eta[-1]] = self.F3(eta[eta <= self.eta[-1]])
        return res

    def defU(self, eta):
        return 1 - self.U(eta)

    def defUint(self, eta):
        return eta - self.Uint(eta)

    def UdefU(self, eta):
        u = self.U(eta)
        return u * (1 - u)

    def UdefUint(self, eta):
        u = self.U(eta)
        return u * (1 - u)

if __name__ == '__main__':
    b = Blasius()
    print(b.defUint(100))
