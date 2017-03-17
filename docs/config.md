ETRM Configuration
==================

Here is an example YAML file that may be used as a template to configure ETRM. 

```yaml
---
input_root: /Volumes/Seagate Expansion Drive

start_date = 12/1/2013
end_date = 12/32/2013

mask: Mask
polygons: Blank_Geo

save_dates: []

daily_outputs:
 - tot_infil
 - tot_etrs
 - tot_eta
 - tot_precip
 - tot_kcb

taw_modification: 1.0

---
input_root: /Volumes/Seagate Expansion Drive

start_date = 12/1/2013
end_date = 12/32/2013

mask: Mask
polygons: Blank_Geo

save_dates: []

daily_outputs:
 - tot_infil
 - tot_etrs
 - tot_eta
 - tot_precip
 - tot_kcb

taw_modification: 0.1
```
