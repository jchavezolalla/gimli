#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DC1dSmooth
---------

This tutorial shows how an built-in forward operator is used for an Occam type
(smoothness-constrained) inversion with fixed regularization (most natural).
A direct current (DC) one-dimensional (1D) VES (vertical electric sounding)
modelling operator is used to generate data, add noise and inversion."""

###############################################################################
# We import numpy numerics, mpl plotting, pygimli and the 1D plotting function
import numpy as np
import matplotlib.pyplot as plt

import pygimli as pg
from pygimli.mplviewer import drawModel1D

###############################################################################
###############################################################################
# initialize the forward modelling operator and compute synthetic noisy data
synres = [100., 500., 20., 800.]  # synthetic resistivity
synthk = [4, 6, 10]  # synthetic thickness (lay layer is infinite)
ab2 = np.logspace(-1, 2, 25)  # 0.1 to 100 in 25 steps (8 points per decade)
fBlock = pg.DC1dModelling(len(synres), ab2, ab2/3)
rhoa = fBlock(synthk+synres)
# The data are noisified using a
errPerc = 3.  # relative error of 3 percent
rhoa = rhoa * (pg.randn(len(rhoa)) * errPerc / 100. + 1.)
###############################################################################
# %% the forward operator can be called by f.response(model) or simply f(model)
thk = np.logspace(-0.5, 0.5, 30)
f = pg.DC1dRhoModelling(thk, ab2, ab2/3)
###############################################################################
# %% create some transformations used for inversion
transRho = pg.RTransLogLU(1, 1000)  # lower and upper bound
transRhoa = pg.RTransLog()  # log transformation also for data
###############################################################################
# set up inversion
inv = pg.RInversion(rhoa, f, transRhoa, transRho, False)  # data vector, f, ...
# The transformations can also be omitted and set individually by
inv.setTransData(transRhoa)
inv.setTransModel(transRho)
###############################################################################
# the error model is set to the above used noise level
inv.setRelativeError(errPerc / 100.0)
###############################################################################
# optionally change default model by changing a layer resistivity
model = pg.RVector(len(thk)+1, np.median(rhoa))  # uniform values
inv.setModel(model)  #
###############################################################################
# set pretty large regularization strength and run inversion
print("inversion with lam=200")
inv.setLambda(100)
res100 = inv.run()  # result is a pg.RVector, but compatible to numpy array
inv.echoStatus()
# We now decrease the regularization (smoothness) and start (from old result)
print("inversion with lam=20")
inv.setLambda(10)
res10 = inv.run()  # result is a pg.RVector, but compatible to numpy array
inv.echoStatus()
# We now optimize lambda such that data are fitted within noise (chi^2=1)
print("chi^2=1 optimized inversion")
resChi = inv.runChi1()  # ends up in a lambda of about 3
inv.echoStatus()
print("optimized lambda value:", inv.getLambda())
###############################################################################
# show everything
fig, ax = plt.subplots(ncols=2, figsize=(8, 6))  # two-column figure
# plot model (inverted and synthetic)
drawModel1D(ax[0], synthk, synres, color='b', label='synthetic',
            plotfunction='semilogx')
drawModel1D(ax[0], thk, res100, color='g', label=r'$\lambda$=100')
drawModel1D(ax[0], thk, res10, color='c', label=r'$\lambda$=10')
drawModel1D(ax[0], thk, resChi, color='r', label=r'$\chi$=1')
ax[0].grid(True, which='both')
ax[0].legend(loc='best')
# plot sounding curve data and model response
ax[1].loglog(rhoa, ab2, 'rx-', label='measured')
ax[1].loglog(inv.response(), ab2, 'b-', label='fitted')
ax[1].set_ylim((max(ab2), min(ab2)))
ax[1].grid(True, which='both')
ax[1].set_xlabel(r'$\rho_a$ [$\Omega$m]')
ax[1].set_ylabel('AB/2 [m]')
ax[1].legend(loc='best')

plt.show()
