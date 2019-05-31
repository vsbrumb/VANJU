                            VANJU 

The VANJU library is a library built in Python 2.7 to help you link movement 
data with contextual data in raster format, like rainfall from radar, satellite 
imagery and NDVI.

With VANJU, users can add estimates of environmental variables to tracking 
data by importing fixes and raster data into a database. 

Please contact vsbrumb@gmail.com for more information and feedback.


Development of VANJU was funded by the Brazilian government and SWB (Science 
Without Borders) - CAPES (Coordination for the Improvement of Higher Education
Personnel).

To acknowledge the use of this package and for more details on the annotation 
methods, please check: 

Brum-Bastos, V.; Long, J. ; Demšar, U. A comparative analysis of dynamic and 
traditional trajectory annotation methods. International Journal of Geographic 
Information Science. Special issue on Computational Movement Analysis(2017).  

REQUIREMENTS 

1 - Software
	A) PostgreSQL 9.3 - Available at : https://www.postgresql.org/download/ 
	B) PostGIS 2.1.3 - Available at: http://postgis.net/
	
2 - Python modules

	A) Psycopg2 2.7.1 - Available at : https://pypi.python.org/pypi/psycopg2
	B) OS * - Available at : https://docs.python.org/3/library/os.html
	C) DateTime * - Available at : https://docs.python.org/2/library/datetime.html
	D) Numpy * - Available at : http://www.numpy.org/
	E) Scipy *- Available at : https://www.scipy.org/
	F) Math * - Available at: https://docs.python.org/2/library/math.html
	
	*These modules are native in most Python 2.7 installations, to check if you have 
	them use import 'module name'.

DEMO

Inside the package there is a folder named DEMO, inside it you will find the 
'demo.shp' and its auxiliary file. This shapefile contains the fixes of a segment of 
annonymized trajectory. You will also find the folder 'Rasters', within it you must have 
eight .tiff files; these are raster data generated with a Gaussian random field for 
testing.

You can use the DEMO data to test the functions before applying it to your dataset. The 
functions and parameters are described in the next section.
	
FUNCTIONS

1) NewDB(port, username, password, DBname)

	This function will create a PostgreSQL database where fixes and rasters will be stored 
	for the next steps. You will also be able to access the database using PgAdmin, a
	database manager that comes with PostgreSQL. 

	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name for your new database.DO NOT USE CAPITALS.
	
DEMO example:

import VANJU
VANJU.NewDB('5432','postgres','postgres','mydemodb')

2) ImportFixes(port, username,password, DBname,table,postgrespath,srcID,shppath)

	This function will create a PostGIS (spatial) extension and a schema named 'gps_data' 
	in the database. A table with the fixes will be stored under the 'gps_data' schema. 
	You will also be able to access the database using PgAdmin, a database manager that 
	comes with PostgreSQL. The input data must be in the shapefile format.

	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name fused in function 1(NewDB).
	- table: The name for the table where the fixes will be stored.
	- postgrespath: The path to the 'bin' folder inside PostgresSQL installation.
	- srcID: the Spatial Reference System Identifier for the coordinates system in which 
		     the fixes are projected. Check http://spatialreference.org/ref/esri/ for a 
			 SRID list if you are unsure about the code for your data.
	- shpath: The path for the shapefile with the fixes, try to keep it as short as possible, 
			  long paths might result in a trace back.
			  
	DO NOT FORGET TO USE '\\' INSTEAD OF '\' WHEN SETTING THE PATHS.

DEMO example:

import VANJU
VANJU.ImportFixes('5432','postgres','postgres','mydemodb','fixes','C:\\Program Files\\PostgreSQL\\9.3\\bin','27700','C:\\DEMO\\demo.shp')

Obs: 27700 is the SRID for the OSGB 1936 / British National Grid system.

3) ImportRaster(port, username,password, DBname,table,postgrespath,srcID,rasterspath)

	This function will create a PostGIS (spatial) extension and a schema named 'gps_data' 
	in the database. A table with the fixes will be stored under the 'gps_data' schema. 
	You will also be able to access the database using PgAdmin, a database manager that 
	comes with PostgreSQL. 

	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name fused in function 1(NewDB).
	- table: The name for the table where the rasters will be stored, must be different from 
			 the one where fixes were stored.
	- postgrespath: The path to the 'bin' folder inside PostgresSQL installation.
	- srcID: the Spatial Reference System Identifier for the coordinates system in which 
		     the rasters are projected. Check http://spatialreference.org/ref/esri/ for a 
			 SRID list if you are unsure about the code for your data.
	- rasterspath: The path for the folder with the raster/rasters you want to use as contextual, 
				   try to keep it as short as possible, long paths might result in a trace back.
				   
				   If you want to import more than one raster, set the path to the folder and add 
				   '\\*rasterextension'. See example below.
				   
		DO NOT FORGET TO USE '\\' INSTEAD OF '\' WHEN SETTING THE PATHS.

DEMO example:
		
import VANJU
VANJU.ImportRaster('5432','postgres','postgres','mydemodb','raster','C:\\Program Files\\PostgreSQL\\9.3\\bin','27700','C:\\DEMO\\Rasters\\*tif')	

Obs: 27700 is the SRID for the OSGB 1936 / British National Grid system.

4) Extract_RTS(port, username,password, DBname,schematable,dateformat, addhours)

	This function will create a field with timestamps for the rasters; this field is based on the
	name of the raster when they were imported. Most raster datasets are named after their data 
	and time of acquisition. Do not worry if the name contain other characters, they will not be 
	considered. 

	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name fused in function 1(NewDB).
	- schematable: The name of the schema and table where the rasters were stored, this is 
				   'raster_data.' + the name you give to your table in function 3. See example below.
	- dateformat: The way the date or date and time is organized in the name of the original raster
				  files. Datasets usually follow a convention, for Landsat data for example see:
				  https://landsat.usgs.gov/what-are-naming-conventions-landsat-scene-identifiers .
				  In this case the dateformat parameter is "'YYYYMMDD'". DO NOT FORGET THE DOUBLE AND
				  SINGLE QUOTATION MARKS.
				  
				  Use Y for year, M for month, D for day, HH24 for hour in the 24h format, HH12 for
				  hour in the 12 format, MI for minutes, SS for seconds. For more details on date 
				  time formatting check Table 9-24 Template Patterns for Date/Time Formatting at
				  https://www.postgresql.org/docs/9.6/static/functions-formatting.html
				  
				  If your original file name does not have time, which is the case for most satellites
				  the system will set the time to 00:00:00 for all images. If you know the time when the
				  image was collected (you can find out on the meta data) you can use the next argument to
				  fix it.
	- addhours: This parameter is optional and the default is zero. If you your original file name does not 
				have time the system will set the time to 00:00:00 for all images. If you know that your 
				raster was collected at 10:45:00, you can add this information by setting this parameter to
				"'10:45:00'". DO NOT FORGET THE DOUBLE AND SINGLE QUOTATION MARKS.

DEMO example:
		
import VANJU				  
VANJU.Extract_RTS('5432','postgres','postgres','mydemodb','raster_data.raster', "'YYYYMMDDHH24MISS'")

5) Intersect(port, username,password, DBname,fixesschema,fixestable, rasterschema, rastertable,tstampfield, tstampformat,variable)

	Based on the fix timestamp this function will  find time t1 (raster time before or at the time the fix
	was collected) and t2 (raster time after), create a variable field for t1 and another one for t2 for
	each fix in the database. The function will then intersect each fix in space with the raster at t1 and
	the raster at t2. 
	
	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name fused in function 1(NewDB).
	- fixesschema: If you created your database using this package the default is 'gps_data'.
	- fixestable: The name you give to your table in function 2. See example below.
	- rasterschema: If you created your database using this package the default is 'raster_data'. 
	- rastertable: The name you give to your table in function 3. See example below.
	- tstampfield: The field in your original fixes table where the timestamps are stored. 
	- tstampformat: The way the date or date and time is organized in the fixes table. Datasets 
				  usually follow a convention, for Landsat data for example see:
				  https://landsat.usgs.gov/what-are-naming-conventions-landsat-scene-identifiers .
				  In this case the dateformat parameter is "'YYYYMMDD'". DO NOT FORGET THE DOUBLE AND
				  SINGLE QUOTATION MARKS.
				  
				  Use Y for year, M for month, D for day, HH24 for hour in the 24h format, HH12 for
				  hour in the 12 format, MI for minutes, SS for seconds. For more details on date 
				  time formatting check Table 9-24 Template Patterns for Date/Time Formatting at
				  https://www.postgresql.org/docs/9.6/static/functions-formatting.html
	- variable: The name for the variable represented by the raster dataset you are intersecting.

DEMO example:
		
import VANJU				  
VANJU.Intersect('5432','postgres','postgres','mydemodb', 'gps_data', 'fixes','raster_data', 'raster', 'tstamp',"'YYYY-MM-DD HH24:MI:SS'",'random')	

6)FindUsers(port,username,password, DBname,uid,fixesschema,fixestable)
	
	This function will find how many users, i.e. different people or animal, are in the fixes table.
	It can be specially helpful when working with many users and there is the need to use parallel 
	computing. FOR PARALLEL COMPUTING SEE ITEM 7 IN THIS MANUAL.
	
	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name used in function 1(NewDB).
	- uid: The field containing the user ids(from your original shapefile).
	- fixesschema: If you created your database using this package the default is 'gps_data'.
	- fixestable: The name you give to your table in function 2. See example below. 
	
DEMO example:
		
import VANJU
				  
user_list = VANJU.FindUsers('5432','postgres','postgres','mydemodb','user_id','gps_data', 'fixes')  

Obs: There is only one user on the demo dataset.	

7) Annotation(port,username, password,DBname,user,tstampfield,variable,fixesschema, fixestable,uid,method,)
	
	This function will calculate the value of the raster at the tim tn when the fix was recorded. The
	calculation is based on the values extracted at t1 and t2. The DTAC method also considers t0 and t3.
	
	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- DBname: The name used in function 1(NewDB).
	- user : One of the users 'i' in the list of user retrieved by function 6.
	- tstampfield: The field in your original fixes table where the timestamps are stored. 
	- variable: The name variable name chosen in function 5.
	- fixesschema: If you created your database using this package the default is 'gps_data'.
	- fixestable: The name you give to your table in function 2. See example below. 
	- uid: The field containing the user ids.
	- method : 
				DTAL: Dynamic Trajectory Annotation - Linear 
				DTAC: Dynamic Trajectory Annotation - Cubic Spline ( Null values will be represented by 9090) 
				NN*:	Nearest Neighbour
				NA*: Neighbour After
				NB*: Neighbour Before
				AM: Arithmetic Mean
	* These methods will also work fro categorical variables.
				
			For more details on how these methods work please check:
					
			Brum-Bastos, V.; Long, J. ; Demšar, U. A comparative analysis of dynamic and 
			traditional trajectory annotation methods. International Journal of Geographic 
			Information Science. Special issue on Computational Movement Analysis(2017). 

DEMO example:
		
import VANJU	

for user in user_list:
	VANJU.Annotation('5432','postgres','postgres','mydemodb',user, 'tstamp','random','gps_data', 'fixes','user_id','AM')
			

IF YOU HAVE A LOT OF USERS AND/OR DATA IT IS PREFERABLE TO USE MULTIPROCESSING

DEMO example:
		
import VANJU	
from multiprocessing import Pool

if __name__ == '__main__':
    p=Pool(3) #Replace X by [(the number of cores in your machine) -1 ]
    print(p.map(VANJU.Annotation('5432','postgres','postgres','mydemodb', user_list,'tstamp','random','gps_data', 'fixes','user_id','AM'), user_list)) 
   
	
8) Export(port,DBname,username, password,fixesschema,fixestable,path,postgrespath,formato)

	This function will export your data with the annotated values, the expored file can have a
	csv or shp extension.
	
	- port: This is the number of the port where you installed PostgreSQL, the default
			 is '5432'.
	- DBname: The name used in function 1(NewDB).
	- username: The username you selected during PostgreSQL installation, the default is 
			   'postgres'.
	- password: The password you selected during PostgreSQL installation.
	- fixesschema: If you created your database using this package the default is 'gps_data'.
	- fixestable: The name you give to your table in function 2. See example below. 
	- path: path to where you waqnt to save the results, including the name and extension for
			the new file. Keep it as short as possible and do not use special characters.
	- postgrespath: The path to the 'bin' folder inside PostgresSQL installation.
	- formato: The format for the output file, valid options are csv and shp.

DEMO example:
		
import VANJU	

VANJU.Export('5432','mydemodb','postgres','postgres','gps_data', 'fixes','I:\\demo.shp', 'C:\\Program Files\\PostgreSQL\\9.3\\bin','shp')
