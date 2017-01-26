# TODO: header

# Version for Windows
grass7bin_win = r'C:\\OSGeo4W64\\bin\\grass72.bat'
#myepsg = '5514'
myfile = ['E:\\janza\\Documents\\grass_skola\\test_vector\\test_vector.shp', 'E:\\janza\\Documents\\grass_skola\\raster_test.tif']
#myfile = 'E:\\janza\\Documents\\grass_skola\\test_vector\\test_vector.shp'
#myfile = 'E:\\janza\\Documents\\grass_skola\\raster_test.tif'

class ErosionBase:
    def __init__(self):
        ###########
        import os
        import sys
        import subprocess
        import shutil
        import binascii
        import tempfile
        import grass.script.setup as gsetup

        self.file_type = None
        self.grass_layer_types = {}
        ########### SOFTWARE
        grass7bin = grass7bin_win

        startcmd = [grass7bin, '--config', 'path']

        p = subprocess.Popen(startcmd, shell=True,
        					 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
            sys.exit(-1)
        str_out = out.decode("utf-8")
        gisbase = str_out
        os.environ['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin', 'sh.exe')

        # Set GISBASE environment variable
        os.environ['GISBASE'] = gisbase
        # define GRASS-Python environment
        gpydir = os.path.join(gisbase, "etc", "python")
        sys.path.append(gpydir)
        gisdb = os.path.join(tempfile.gettempdir(), 'grassdata')
        try:
            os.stat(gisdb)
        except:
            os.mkdir(gisdb)

        # location/mapset: use random names for batch jobs
        string_length = 16
        location = binascii.hexlify(os.urandom(string_length))
        mapset   = 'PERMANENT'
        location_path = os.path.join(gisdb, location)

        # Create new location (we assume that grass7bin is in the PATH)
        #  from EPSG code:
        #startcmd = grass7bin + ' -c epsg:' + myepsg + ' -e ' + location_path
        #  from SHAPE or GeoTIFF file
        startcmd = grass7bin + ' -c ' + myfile + ' -e ' + location_path

        p = subprocess.Popen(startcmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            print >>sys.stderr, 'ERROR: %s' % err
            print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
            sys.exit(-1)
        else:
            print 'Created location %s' % location_path

        ###########
        # launch session
        gsetup.init(gisbase, gisdb, location, mapset)

    def import_files(files):
    	for i in range(len(files)):
    		file_type = file_type_test(files[i])
    		file_name = os.path.basename(files[i]).split(".")[0]
    		assert file_name not in grass_layer_types, "Layer {} already imported".format(file_name)
    		grass_layer_types[file_name] = file_type
    		print(grass_layer_types)
    		import_data(files[i], file_type, file_name)

    def import_data(self, file, file_type, file_name):
    	#import
    	if file_type == 'raster':
    		r.external(input=file, output=file_name)
    	elif file_type == 'vector':
    		g.message("Importing SHAPE file ...")
    		ogrimport = Module('v.in.ogr')
    		ogrimport(file, output=file_name)
    	else:
    		pass

        #messages
        gscript.message('Current GRASS GIS 7 environment:')
        print(gscript.gisenv())

        gscript.message('Available raster maps:')
        for rast in gscript.list_strings(type = 'rast'):
            print(rast)

        gscript.message('Available vector maps:')
        for vect in gscript.list_strings(type = 'vect'):
            print(vect)


    def export_data(self, grass_file, o_path, o_name):
    	out_file = os.path.join(o_path, o_name)
    	#v.out_ogr(input=in_file, output=out_file, type='auto', format='ESRI_Shapefile')

def file_type_test(file):
    #Vector test
    src_ds = ogr.Open(file)
    if src_ds:
        file_type = 'vector'
    #Raster test
    if not file_type:
        src_ds = gdal.Open(file)
        if src_ds:
            file_type = 'raster'
    return file_type
