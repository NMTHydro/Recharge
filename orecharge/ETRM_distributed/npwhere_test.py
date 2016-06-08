import numpy as np

k = 0.12
temp = np.random.randn(10, 10)
zeros = np.zeros(temp.shape)
ones = np.ones(temp.shape)
ppt = np.random.randn(10, 10) + 3.0
a_max = np.ones(temp.shape) * 0.95
a_min = a_max - 0.5
a = a_max - 0.2

snow_fall = np.where(temp <= 0.0, ppt, zeros)
rain = np.where(temp >= 0.0, ppt, zeros)
for x in range(1, 25):
    pA = a
    a = np.where(snow_fall > 3.0, ones * a_max, a)
    a = np.where(snow_fall < 3.0, a_min + (pA - a_min) * np.exp(-k), a)
    a = np.where(a < a_min, a_min, a)
    print a

ksat = np.random.randn(10, 10) + 5
ksat = np.where(ksat < 0.0, 0.0, ksat)
watr = ones * 3.0
deps = ones * 2.5
dk = deps + ksat

ro = zeros
ro = np.where(watr > ksat + deps, watr - ksat - deps, ro)
dp_r = zeros
dp_r = np.where(ksat > watr - deps, np.maximum(watr - deps, zeros), dp_r)
dp_r = np.where(watr > ksat + deps, ksat, dp_r)
