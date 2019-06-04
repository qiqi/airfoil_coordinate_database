from blasius import Blasius

b = Blasius()
defUint = b.defUint(10)


delta = logspace(-.8,.5,801)
U1 = b.U(defUint / delta)
dUdy1 = b.dUdy(defUint / delta) * defUint / delta
U0 = U1 - dUdy1
invLp = dUdy1 / U0

figure(figsize=(16,16))
loglog(delta, invLp, '-b')

pwr0 = -3
pwr1 = -5

loglog(delta, (2.115*delta)**3 * exp(-(2.62 * delta)**pwr0 - (4.6 * delta)**pwr1), '--')
ylim([1E-2, 1E2])
grid()

twinx()
semilogx(delta, (2.115*delta)**3 * exp(-(2.62 * delta)**pwr0 - (4.6 * delta)**pwr1) / invLp, '--')

