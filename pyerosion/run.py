#!/usr/bin/env python

from erosionbase import ErosionBase
from grass.script import core as grass

er = ErosionBase()
er.import_files(['data\\hpj.shp',
                'data\\kpp.shp',
                'data\\landuse.shp',
                'data\\povodi.shp',
                'data\\hpj_hydrsk.csv',
                'data\\kpp_hydrsk.csv',
                'data\\lu_hydrsk_cn.csv',
                ])

def run (out_file):
    grass.run_command("v.overlay", ainput='hpj', binput='kpp', operator='or', output='hpj_kpp')

    grass.run_command("db.execute", sql='alter table hpj_hydrsk add column HPJ_key int;')
    grass.run_command("db.execute", sql='update hpj_hydrsk set HPJ_key = cast(HPJ as int);')

    grass.run_command("v.db.join", map='hpj_kpp', column='a_HPJ', other_table='hpj_hydrsk', other_column='HPJ')

    grass.run_command("db.execute", sql='update hpj_kpp SET HydrSk = (SELECT b.HydrSk FROM hpj_kpp AS a JOIN kpp_hydrsk as b ON a.b_KPP = b.KPP) WHERE HydrSk IS NULL;')

    grass.run_command("v.db.addcolumn", map='hpj_kpp', columns='HydrSk_key int')
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 1 where HydrSk = 'A';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 2 where HydrSk = 'AB';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 3 where HydrSk = 'B';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 4 where HydrSk = 'BC';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 5 where HydrSk = 'C';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 6 where HydrSk = 'CD';")
    grass.run_command("db.execute", sql="update hpj_kpp set HydrSk_key = 7 where HydrSk = 'D';")

    grass.run_command("g.region", vector='hpj_kpp', res=10)

    grass.run_command("v.overlay", ainput='hpj_kpp', binput='landuse', operator='and', output='hpj_kpp_land')

    grass.run_command("v.db.addcolumn", map='hpj_kpp_land', columns='LU_HydrSk text')
    grass.run_command("db.execute", sql="update hpj_kpp_land set LU_HydrSk = b_LandUse || '_' || a_HydrSk;")

    grass.run_command("v.db.join", map='hpj_kpp_land', column='LU_HydrSk', other_table='lu_hydrsk_cn', other_column='LU_HydrSk', subset_columns='CN')
    grass.run_command("g.region", vector='hpj_kpp_land', res=10)

    grass.run_command("v.overlay", ainput='hpj_kpp_land', binput='povodi', operator='or', output='hpj_kpp_land_pov')

    grass.run_command("v.db.addcolumn", map='hpj_kpp_land_pov', columns="vymera double,A double,I_a double")
    grass.run_command("v.to.db", map='hpj_kpp_land_pov', option='area', columns='vymera')
    grass.run_command("v.db.update", map='hpj_kpp_land_pov', column='A', value="24.5 * (1000 / a_CN - 10)")
    grass.run_command("v.db.update", map='hpj_kpp_land_pov', column='I_a', value="0.2 * A")

    grass.run_command("v.db.addcolumn", map='hpj_kpp_land_pov', columns="HOklad double, HO double, OP double")
    grass.run_command("v.db.update", map='hpj_kpp_land_pov', column='HOklad', value="(32 - 0.2 * A)")
    grass.run_command("db.execute", sql="update hpj_kpp_land_pov set HOklad = 0 where HOklad < 0;")
    grass.run_command("v.db.update", map='hpj_kpp_land_pov', column='HO', value="(HOklad * HOklad) / (32 + 0.8 * A)")

    grass.run_command("v.db.update", map='hpj_kpp_land_pov', column='OP', value="vymera * (HO / 1000)")

    grass.run_command("g.region", vector='kpp', res=10)

    grass.run_command("db.execute", sql="create table hpj_kpp_land_pov1 as select cat,HO,OP from hpj_kpp_land_pov;")
    grass.run_command("db.execute", sql="drop table hpj_kpp_land_pov;")
    grass.run_command("db.execute", sql="alter table hpj_kpp_land_pov1 rename to hpj_kpp_land_pov;")

    grass.run_command("v.out.ogr", input='hpj_kpp_land_pov', output=out_file)

output_file = 'E:\\janza\\Documents\\grass_skola\\hpj_kpp_land_pov.shp'
run(output_file)

er.test()
