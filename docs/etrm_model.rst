ETRM Model
==========

How Dual Crop Coefficients are calculated
-----------------------------------------
See :meth:`recharge.etrm_processes.Processes._do_dual_crop_coefficient`

The well-established FAO Penman-Monteith dual crop coefficient(DCC) method finds a reference evapotranspiration
value from which actual transpiration can be derived.  See GADGET documentation for a description of tall crop
reference ET (etrs). By accounting for soil water, actual evapotranspiration (eta) can be estimated by
calculating a stress factor coefficient Ks, a basal vegetation transpiration coefficient Kcb, and a bare
surface evaporation coefficient Ke, and multiplying them by etrs. This method is known
as the dual-crop-coefficient method (Allan et al., 1998).  Jensen and others (1990) found that of 20 ET
estimation methods, results varied considerably in varying climates and showed the need for rigorous
and expensive calibration methods when a method developed in one climate was then applied to another.
The FAO Penman-Monteith was devised in the 1990s as a method that needed less rigorous local
calibration than other, more empirical and local methods such as the BCM and INFIL.  The operational
goal of the method is to find a constrained and reasonable estimate of ET with a minimum of climate data
inputs.  The method contains many possible variations to allow for the continuation of the ET calculation
despite missing or incomplete data.  Jabloun and Sahli (2008) found that use of FAO-56 recommended
methods of calculating ET with missing data produced results close to those found using complete data.

This dual crop coefficient makes use of a modified skin layer evaporation mechanism, as described in
Allen (2011).  This has the cost of added uncertainty in the skin layer thickness and rew terms but
the benefit of modeling the rapid evaporation that occurs after a small wetting event, which is limited
only by available energy.

The initial calculations are a roundabout way of finding the fraction of the ground that is covered
by vegetation (fcov) and that which is not (few).  The exponent is intended to account for the effect
that plant height has on shading the ground.  The equation has the implicit assumption that kcb
is controlled by the fraction of vegetative cover, which at this time is calculated with the NDVI. In
a locale with only bare soil, fcov = 0.01, few = 0.99.

To find transpiration, the DCC calculates a root-zone transpiration stress coefficient, Ks. Ks depends
on the amount of water in the root zone relative to water capacity, taw.  If the root zone is in a state
of maximum water (i.e., at field capacity), there is no limit on transpiration by the soil. Therefore Ks is
one.  As the root zone is depleted of water by transpiration, the soil dries, increasing the depletion (dr).
As the difference between depletion and taw increases, Ks decreases, causing a reduction in the rate
of transpiration. The basal crop coefficient (kcb) is simply the ratio of ET from a specific crop
compared to the reference ET given current meteorological conditions. Kcb ranges from zero for a
dry soil losing no water to ET, to perhaps 1.20 for a well watered crop transpiring at a high rate.
The final factor needed to estimate transpiration is the tall crop reference ET (etrs).  This is the
rate of ET for a well watered crop of alfalfa, 0.5 m height, in good growing conditions.  See GADGET
documentation for details and derivation.

To find evaporation, the ETRM makes use of the common differentiation of stage one and stage two evaporation.
Stage one evaporation is the vaporization of water of which the rate is controlled principally by
atmospheric conditions.  Thus, available energy in the form of radiation and sensible heat, and the
aerodynamic effects of wind and surface texture. This process is not controlled by soil water content;
the conditions immediately above the soil control the rate of evaporation.  Stage two evaporation
is controlled by the process of diffusion of water vapor through the soil.  The water vapor pressure gradient
upwards from damp soil to drier soil at the surface controls the rate at which water leaves the soil.
Therefore, if the soil is very wet at some depth, but very dry at a shallower depth, the process will occur
at a greater rate than if the underlying soil was drier, as the gradient is greater. The ETRM attempts to
model this process.