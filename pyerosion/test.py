#!/usr/bin/env python

from erosionbase import ErosionBase

er = ErosionBase()
er.import_files(['/home/landa/geodata/shp/ruian/kraje.shp',
                 '/home/landa/geodata/dmt_ltm.tif'])
er.test()
