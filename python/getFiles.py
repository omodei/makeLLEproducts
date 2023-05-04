#!/usr/bin/env python
import os
cmd='xrdcp root://glast-rdr//glast/mc/ServiceChallenge/SolarFlare-GR-v17r35p1/merit/SolarFlare-GR-v17r35p1-%06d-merit.root .'

for i in range(100):
    os.system(cmd % i)
    pass

