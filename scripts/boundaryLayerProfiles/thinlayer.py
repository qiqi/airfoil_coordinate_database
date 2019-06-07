import os
import pdb
import subprocess

from pylab import *
from numpy import *
from scipy.sparse import csr_matrix, dia_matrix
from scipy.sparse import eye as speye
from scipy.sparse import linalg as splinalg

def invLslip(delta):
    pwr0, pwr1 = -3, -5
    return (2.115*delta)**3 * exp(-(2.62 * delta)**pwr0 - (4.6 * delta)**pwr1)

def ddy_ops(y, Lslip):
    n = y.size - 1
    v = zeros(n+1)
    dy = y[1:] - y[:-1]

    yc = (y[1:] + y[:-1]) / 2
    dyc = yc[1:] - yc[:-1]

    ddy_data = hstack([1./ dy, -1./ dy])
    ddy_i = hstack([arange(n), arange(n)])
    ddy_j = hstack([arange(1,n+1), arange(n)])
    ddy_node_op = csr_matrix((ddy_data, (ddy_i, ddy_j)), (n,n+1))

    ddy_data = hstack([1. / (yc[0] + Lslip),
                       1. / (yc[1:] - yc[:-1]),
                      -1. / (yc[1:] - yc[:-1])])
    ddy_i = hstack([0, arange(1,n), arange(1,n)])
    ddy_j = hstack([0, arange(1,n), arange(n-1)])
    ddy_cell_op = csr_matrix((ddy_data, (ddy_i, ddy_j)), (n+1,n))
    return ddy_node_op, ddy_cell_op

def stepFlatPlate(y, dx, uc0, nuLam=1, Lslip=0, maxIter=50, tol=1E-8):
    dy = y[1:] - y[:-1]
    vol = hstack([dy[0]/2, (dy[1:]+dy[:-1])/2, dy[-1]/2])
    n = y.size - 1
    yc = (y[1:] + y[:-1]) / 2
    ddy_node_op, ddy_cell_op = ddy_ops(y, Lslip)

    uc = uc0.copy()
    for iIter in range(maxIter):
        dudx = (uc - uc0) / dx
        dudy = ddy_cell_op * uc

        dv = -dudx * dy
        v = hstack([0, cumsum(dv)])
        v_dudy = v * dudy

        jac_u = ddy_node_op \
              * dia_matrix((nuLam * ones(n+1), 0), (n+1,n+1)) \
              * ddy_cell_op
        res_u = jac_u * uc
        jac_u -= dia_matrix(((2 * uc - uc0) / dx, 0), (n, n))
        res_u -= uc * dudx
        res_u -= (v_dudy[1:] + v_dudy[:-1]) / 2

        d_uc = -splinalg.spsolve(jac_u, res_u)
        uc += d_uc

        if linalg.norm(d_uc) < tol:
            return uc
        elif linalg.norm(d_uc) > 1E8:
            raise RuntimeError("Diverged")
    return uc

def boundaryLayerThickness(y, uc):
    dy = y[1:] - y[:-1]
    uc = uc / uc[-1]
    deltaStar = sum((1 - uc) * dy)
    theta = sum((1 - uc) * uc * dy)
    delta99 = y[searchsorted(uc, 0.99)]
    return deltaStar, theta, delta99

if __name__ == '__main__':
    n = 130
    x = 0
    dy = logspace(0, 8, n)
    y = hstack([0, cumsum(dy)])
    yc = (y[1:] + y[:-1]) / 2

    uc = ones(n)

    Rex, thickness, cf = [], [], []
    figure(figsize=(20,20))
    for i in range(100):
        dx = max(0.001, x * 0.08)
        Lslip = 1./ invLslip(1.72 * sqrt(x + dx))
        uc = stepFlatPlate(y, dx, uc, Lslip=Lslip)
        x += dx
        Rex.append(x)
        thickness.append(boundaryLayerThickness(y, uc))
        cf.append(2 * uc[0] / (yc[0] + Lslip))

        if (i+1)%10 == 0:
            print('x={:.1e}'.format(x))
            subplot(2,10,(i+1)//10)
            plot(hstack([0, uc]), hstack([-Lslip, yc]), '.-')
            fill_between([0,1.1], [0,0], 1.72 * sqrt(x + dx) * ones(2),
                         alpha=0.2, color='r')
            xlim([0,1.1])
            ylim([0,10])
            grid()
            title('{:.1g}'.format(x))

    Rex = array(Rex[1:])
    thickness = array(thickness[1:])
    H = thickness[:,0] / thickness[:,1]
    cf = array(cf[1:])

    subplot(2,2,3)
    loglog(Rex, thickness)
    #loglog(Rex, 0.01 * Rex**(1-1./7), '--')
    grid()
    xlabel(r'$Re_x$')
    loglog(Rex, cf, 'k')
    loglog(Rex, 1.72 * sqrt(Rex), '.')
    loglog(Rex, 2 * 0.332 / sqrt(Rex), '.k')
    #loglog(Rex, 0.02/Rex**(1./7), '--k')
    ylim([0.1, 10])
    xlim([0.01, 10])
    legend([r'$\delta^*$', r'$\theta$', r'$\delta_{99}$', r'$C_f$'])

    subplot(2,2,4)
    semilogx(Rex, H)
    grid()
    xlabel(r'$Re_x$')
    ylabel(r'$H$')

    subplot(2,10,1)
    ylabel(r'$U$')
    savefig('flatplate.png')
'''
    saveFig('testFlatPlate.png')

    laminar = logical_and(10 < Rex, Rex < 5000)
    assert(abs(H[laminar] - 2.59).max() < 0.15)
    deltaStarTheoretical = 1.72 * sqrt(Rex[laminar])
    assert(abs(thickness[laminar,0] / deltaStarTheoretical - 1).max() < 0.1)
    cfTheoretical = 2 * 0.332 / sqrt(Rex[laminar])
    assert(abs(cf[laminar] / cfTheoretical - 1).max() < 0.05)

    turbulent = (Rex > 2E5)
    assert(H[turbulent].max() < 1.8)
    deltaStarTheoretical = 0.02 * Rex[turbulent] / Rex[turbulent]**(1./7)
    assert(abs(thickness[turbulent,0] / deltaStarTheoretical - 1).max() < 0.25)
    thetaTheoretical = 0.016 * Rex[turbulent] / Rex[turbulent]**(1./7)
    assert(abs(thickness[turbulent,1] / thetaTheoretical - 1).max() < 0.2)
    cfTheoretical = 0.027 / Rex[turbulent]**(1./7)
    assert(abs(cf[turbulent] / cfTheoretical - 1).max() < 0.2)
'''

