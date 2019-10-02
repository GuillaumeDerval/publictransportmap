import os
import subprocess
import tempfile

LEVEL_INCREMENT = 5
MIN_LEVEL = 0
MAX_LEVEL = 100

input_file = "sncbS8814001.speed.tif"

tmpdir = tempfile.mkdtemp()
print(tmpdir)
for level in range(MIN_LEVEL, MAX_LEVEL+1, LEVEL_INCREMENT):
    if level == MIN_LEVEL:
        cond = "A<{}".format(level+5)
    elif level == MAX_LEVEL:
        cond = "A>={}".format(level)
    else:
        cond = "(A<{})&(A>={})".format(level+5, level)

    c = ["gdal_calc.py", "--NoDataValue=0", "-A", input_file, "--calc={}".format(cond), "--quiet", "--outfile", "{}/tmp_{}.tif".format(tmpdir, level)]
    print(" ".join(c))
    subprocess.call(c)

    c = ["gdal_polygonize.py", "-q", "-f", "ESRI Shapefile", "{}/tmp_{}.tif".format(tmpdir, level), "{}/tmp_{}.shp".format(tmpdir, level)]
    print(" ".join(c))
    subprocess.call(c)

    os.unlink("{}/tmp_{}.tif".format(tmpdir, level))

    c = ["ogr2ogr", "-q", "{}/tmp_{}_speed.shp".format(tmpdir, level),
         "{}/tmp_{}.shp".format(tmpdir, level), "-sql", "SELECT {} as speed FROM tmp_{}".format(level, level)]
    print(" ".join(c))
    subprocess.call(c)

    if level == MIN_LEVEL:
        c = ["ogr2ogr", "-f", 'ESRI Shapefile', "{}/merge.shp".format(tmpdir), "{}/tmp_{}_speed.shp".format(tmpdir, level)]
    else:
        c = ["ogr2ogr", "-f", 'ESRI Shapefile', "-update", "-append", "{}/merge.shp".format(tmpdir), "{}/tmp_{}_speed.shp".format(tmpdir, level), "-nln", "merge"]
    print(" ".join(c))
    subprocess.call(c)

c = ["ogr2ogr", "{}/merge.json".format(tmpdir), "{}/merge.shp".format(tmpdir), "-f", "GeoJSON", "-t_srs", "EPSG:4326"]
print(" ".join(c))
subprocess.call(c)