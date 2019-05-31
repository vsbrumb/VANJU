# -*- coding: utf-8 -*-

def NewDB(port, username, password, DBname):
    
    import psycopg2
    
     
    try:
        
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='postgres' user='%s' password=%s" %(port,username,password))
        conn.set_isolation_level(0)
        print'Yay!!! Connection is succesfully stablished!!!'
        
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE %s'%(DBname)) 
        conn.commit()
        cursor.close()
        conn.close()
        print  'Database was created!'        
        
    except (Exception, psycopg2.DatabaseError) as error:
        
        print error
 
def ImportFixes(port, username,password, DBname,table,postgrespath,srcID,shppath):
        import psycopg2
        try:
        
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
            
            cursor = conn.cursor()
            cursor.execute("CREATE EXTENSION postgis")
            cursor.execute("CREATE SCHEMA IF NOT EXISTS gps_data")
            conn.commit()
            cursor.close()
            conn.close()
     
        
        except (Exception, psycopg2.DatabaseError) as error:
        
           print error
    
        import os
        os.chdir(postgrespath)
        os.system(('shp2pgsql -s %s -c %s gps_data.%s | psql -h localhost -p %s -d %s -U %s')%(srcID, shppath, table,port,DBname,username))

def ImportRaster(port, username,password, DBname,table,postgrespath,srcID,rasterspath):
        import psycopg2
        try:
        
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
                    
            cursor = conn.cursor()
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raster_data")
            conn.commit()
            cursor.close()
            conn.close()
     
        
        except (Exception, psycopg2.DatabaseError) as error:
        
           print error
    
        import os
        os.chdir(postgrespath)
        os.system(('raster2pgsql -s %s -t auto -C -P -F -c %s raster_data.%s | psql -h localhost -p %s -d %s -U %s')%(srcID, rasterspath, table,port,DBname,username))

def Extract_RTS(port, username,password, DBname,schematable,dateformat, addhours='0 hours' ):
        import psycopg2
        try:
        
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
                    
            cursor = conn.cursor()
            
            cursor.execute("ALTER TABLE %s ADD COLUMN timestring VARCHAR"%(schematable))
            conn.commit()
            
            cursor.execute("UPDATE %s SET timestring = regexp_replace(filename, '\D', '', 'g') "%(schematable))
            conn.commit()
            
            cursor.execute("ALTER TABLE %s ADD COLUMN timestamp TIMESTAMP WITHOUT TIME ZONE"%(schematable))
            conn.commit()
            
            cursor.execute("UPDATE %s SET timestamp = to_timestamp(timestring, %s )"%(schematable, dateformat))
            conn.commit()                 
                 
            if addhours != '0 hours':
                
                cursor.execute("UPDATE %s SET timestamp = (timestamp + interval '%s ')"%(schematable, addhours))
                conn.commit()                 
                
            cursor.close()
            conn.close()
                
        
        except (Exception, psycopg2.DatabaseError) as error:
        
           print error
    
    
def Intersect(port, username,password, DBname,fixesschema,fixestable, rasterschema, rastertable,tstampfield, tstampformat,variable):
        import psycopg2
        try:
        
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
                    
            cursor = conn.cursor()
            
            cursor.execute("ALTER TABLE %s ADD COLUMN t1 TIMESTAMP WITHOUT TIME ZONE"%((fixesschema+'.'+fixestable)))
            conn.commit()
            cursor.execute('ALTER TABLE %s ADD COLUMN t2 TIMESTAMP WITHOUT TIME ZONE'%((fixesschema+'.'+fixestable)))
            conn.commit()
            
            cursor.execute("SELECT DISTINCT timestamp FROM %s ORDER BY timestamp"%(rasterschema+'.'+rastertable))
            results=cursor.fetchall()
            
            
            timestamps=[]
            for i in results:
                timestamps.append(i[0])
            timestamps.sort()
            
            del results
            
            cursor.execute("ALTER TABLE %s ALTER COLUMN %s TYPE timestamp without time zone USING to_timestamp(%s, %s)"%((fixesschema+'.'+fixestable),tstampfield,tstampfield,tstampformat))
            conn.commit()
         
            cursor.execute("SELECT gid,%s FROM %s ORDER BY gid"%(tstampfield,(fixesschema+'.'+fixestable)))
            fixesstamps=cursor.fetchall()
            
            from datetime import timedelta
            for j in fixesstamps:
                
                k=0
                delta= timedelta(days=1000) 
        
                while (abs(timestamps[k]-j[1]))<delta and k<((len(timestamps)-1)):
                    delta=abs(timestamps[k]-j[1])
                    k=k+1       
                              
                
                if k ==0 and k == (len(timestamps)-1):
                    tn=timestamps[k]
                    t2= tn
                    t1= tn
                  
                elif k==0:
                   tn=timestamps[k]
                   t2= timestamps[k+1]
                   t1= tn
                    
                elif k==1: 
                    tn=timestamps[k-1]
                    t2= timestamps[k]
                    t1= tn
                    
                elif k == (len(timestamps)-1): 
                    tn=timestamps[k]
                    t2= tn
                    t1= timestamps[k-1]
                    
                else:
                    tn=timestamps[k-1]
                    t2= timestamps[k]
                    t1= timestamps[k-2]
            
                if tn<=j[1]:
                    
                    cursor.execute("UPDATE %s SET t1= '%s' WHERE gid= %s"%((fixesschema+'.'+fixestable),tn, j[0]))
                    conn.commit()  
                    cursor.execute("UPDATE %s SET t2= '%s' WHERE gid= %s"%((fixesschema+'.'+fixestable),t2, j[0]))
                    conn.commit()  
                else:
                    cursor.execute("UPDATE %s SET t1= '%s' WHERE gid= %s"%((fixesschema+'.'+fixestable),t1, j[0]))
                    conn.commit()  
                    cursor.execute("UPDATE %s SET t2= '%s' WHERE gid= %s"%((fixesschema+'.'+fixestable),tn, j[0]))
                    conn.commit()  
                    
               
            cursor.execute("ALTER TABLE %s  ADD COLUMN %st1 varchar"%((fixesschema+'.'+fixestable),variable))
            conn.commit()   
            
            cursor.execute("ALTER TABLE %s  ADD COLUMN %st2 varchar"%((fixesschema+'.'+fixestable),variable))
            conn.commit()         
             
            cursor.execute("UPDATE %s  SET %st1 =(ST_Value(%s.rast,%s.geom)) FROM %s  WHERE ST_intersects(geom,rast) and t1=timestamp"%((fixesschema+'.'+fixestable),variable,rastertable,fixestable,(rasterschema+'.'+rastertable)))        
            conn.commit()     
                
            cursor.execute("UPDATE %s  SET %st2 =(ST_Value(%s.rast,%s.geom)) FROM %s  WHERE ST_intersects(geom,rast) and t2=timestamp"%((fixesschema+'.'+fixestable),variable,rastertable,fixestable,(rasterschema+'.'+rastertable))) 
            conn.commit()
                  
            cursor.close()
            conn.close()
                                
        except (Exception, psycopg2.DatabaseError) as error:
                
            print error
        
            
def FindUsers(port,username,password, DBname,uid,fixesschema,fixestable):
    import psycopg2
        
    try: 
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
        conn.set_isolation_level(0)
        cursor = conn.cursor()
  
        cursor.execute("SELECT DISTINCT %s FROM %s ORDER BY %s"%(uid,(fixesschema+'.'+fixestable),uid))
        results = cursor.fetchall()
        
        users=[]
        for l in results:
            users.append(l[0])  
        return users
           
    except (Exception, psycopg2.DatabaseError) as error:
        print error
def Annotation(port,username, password,DBname,user,tstampfield,variable,fixesschema, fixestable,uid,method): 
    import psycopg2

                 
    if method=='DTAL':
        def dynamic(res,R1,R2):
            return (R2-R1)/(res) 
        
        try:
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
            cursor = conn.cursor()
        
            
            cursor.execute("SELECT gid,%s,t1,t2,%st1,%st2 FROM %s WHERE %s= cast(%s as varchar) ORDER BY %s"%(tstampfield,variable,variable,(fixesschema+'.'+fixestable),uid,user,tstampfield))
            records=cursor.fetchall()
    
            fixes=[]
            for j in records:
                fixes.append(j)
        
        except(Exception, psycopg2.DatabaseError) as error:
              
            print error
        
        cursor.execute("ALTER TABLE %s ADD COLUMN dtal double precision"%((fixesschema+'.'+fixestable)))
        conn.commit()
        fail=[]
        for row in fixes:
            try:
                pkey= row[0]
                tn= row[1]
                t1=row[2]
                t2=row[3]
                vt1=float(row[4])
                vt2=float(row[5])
            #%% 
                r=t2-t1
                rsec=r.total_seconds()
            
                if rsec == 0:
                    cursor.execute("UPDATE %s SET dtal =%s WHERE gid = %s"%((fixesschema+'.'+fixestable),vt1,pkey))
                    conn.commit()
                
                else:
                    K= dynamic(rsec,vt1,vt2)
                    tdelta=tn-t1
                    t=tdelta.total_seconds()
                    raindy=(K*t)+vt1
                    
                #%%    
                    cursor.execute("UPDATE %s SET dtal =%s WHERE gid = %s"%((fixesschema+'.'+fixestable),raindy,pkey))
                    conn.commit()
                
            except:
                fail.append(pkey)
        return 'Done!'
        return fail                    

    elif method=='DTAC':
        import numpy as np
        def spline(xi, x_points,y_points):
            from scipy import interpolate
            tck = interpolate.splrep(x_points, y_points)
            return interpolate.splev(xi, tck)
                        
        try:
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
            cursor = conn.cursor()
            
                
            cursor.execute("SELECT gid,%s,t1,t2,%st1,%st2 FROM %s WHERE %s= cast(%s as varchar) ORDER BY %s"%(tstampfield,variable,variable,(fixesschema+'.'+fixestable),uid,user,tstampfield))
            records=cursor.fetchall()
    
            fixes=[]
            for j in records:
                fixes.append(j)
            
        
        except(Exception, psycopg2.DatabaseError) as error:
              
            print error        
                    
        cursor.execute("ALTER TABLE %s ADD COLUMN dtac double precision"%((fixesschema+'.'+fixestable)))
        conn.commit()

        cursor.execute("SELECT DISTINCT t1 FROM %s WHERE %s= (cast(%sAS VARCHAR)) ORDER BY t1"%((fixesschema+'.'+fixestable),uid,user))
        records2 = cursor.fetchall()
        
        tstamps=[]
        for z in records2:
            tstamps.append(z[0])
        
        del(records2)            
        
        for row in fixes:

            t1=row[2]
                
            indexlt1=[i for i,x in enumerate(tstamps) if x == t1]
            indext1=indexlt1[0]
            
            n= len(tstamps)
    
            if indext1 ==0 and indext1 == (len(tstamps)-1):
                
                t0=tstamps[0]
                t1=tstamps[0]
                t2=tstamps[0]
                t3=tstamps[0]
                
                vts0= [item[4] for item in records if item[2] == t0]
                vts1= [item[4] for item in records if item[2] == t1]
                vts2= [item[4] for item in records if item[2] == t2]
                vts3= [item[4] for item in records if item[2] == t3] 
            
            elif indext1 == 0:
                t0=tstamps[0]
                t1=tstamps[1]
                t2=tstamps[2]
                t3=tstamps[3]
                
                vts0= [item[4] for item in records if item[2] == t0]
                vts1= [item[4] for item in records if item[2] == t1]
                vts2= [item[4] for item in records if item[2] == t2]
                vts3= [item[4] for item in records if item[2] == t3] 
               
            
            elif indext1 > (n-3):
                t0=tstamps[n-4]
                t1=tstamps[n-3]
                t2=tstamps[n-2]
                t3=tstamps[n-1]
                
                vts0= [item[4] for item in records if item[2] == t0]
                vts1= [item[4] for item in records if item[2] == t1]
                vts2= [item[4] for item in records if item[2] == t2]
                vts3= [item[4] for item in records if item[2] == t3] 
            else:
                t0=tstamps[indext1-1]
                t1=tstamps[indext1]
                t2=tstamps[indext1+1]
                t3=tstamps[indext1+2]
                
                vts0= [item[4] for item in records if item[2] == t0]
                vts1= [item[4] for item in records if item[2] == t1]
                vts2= [item[4] for item in records if item[2] == t2]
                vts3= [item[4] for item in records if item[2] == t3]
    
                       
            tn= row[1] # This is the time for which I want to find out the value of the variable
            
           
            vt0=vts0[0] #These are the four consecutive values starting at the first available timestamp before the  tn
            vt1=vts1[0]
            vt2=vts2[0]
            vt3=vts3[0]
            
            pkey=row[0]
                    
            #Tranforming from timestamp to seconds interval
            ti=(tn-t0).total_seconds()
            i0=0
            i1=(t1-t0).total_seconds()
            i2=(t2-t0).total_seconds()
            i3=(t3-t0).total_seconds()
            
            
            x=np.array([i0,i1,i2,i3])      
            y=np.array([vt0,vt1,vt2,vt3])   
             
            vti= spline(ti, x,y)

            import math
            if math.isnan(vti)is True:
                             
                cursor.execute("UPDATE %s SET dtac = 9090 WHERE gid = %s"%((fixesschema+'.'+fixestable),pkey))
                conn.commit()
            
            else:
                             
                cursor.execute("UPDATE %s SET dtac = %s WHERE gid = %s"%((fixesschema+'.'+fixestable),vti,pkey))
                conn.commit()
  
    elif method=='NN':
        
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE %s ADD COLUMN nn varchar"%((fixesschema+'.'+fixestable)))
        conn.commit()
           
        cursor.execute("UPDATE %s SET nn = %st1  WHERE (tstamp-t1)<=(t2-tstamp)"%((fixesschema+'.'+fixestable),variable))
        conn.commit()
        
        cursor.execute("UPDATE %s SET nn = %st2  WHERE (tstamp-t1)>(t2-tstamp)"%((fixesschema+'.'+fixestable),variable))
        conn.commit()
        
      
    elif method=='NB':
        
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE %s ADD COLUMN nb varchar"%((fixesschema+'.'+fixestable)))
        conn.commit()
             
        cursor.execute("UPDATE %s SET nb = %st1  "%((fixesschema+'.'+fixestable),variable))
        conn.commit()
        
        cursor.close()    

    elif method=='NA':
        
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE %s ADD COLUMN na varchar"%((fixesschema+'.'+fixestable)))
        conn.commit()
        
        cursor.execute("UPDATE %s SET na = %st2  "%((fixesschema+'.'+fixestable),variable))
        conn.commit()
        
        cursor.close()
              
    elif method=='AM':
        conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        
        cursor.execute("ALTER TABLE %s ADD COLUMN am double precision"%((fixesschema+'.'+fixestable)))
        conn.commit()
        
        cursor.execute("UPDATE %s SET am = ((cast(%st1 as double precision)+(cast(%st2 as double precision)))/2) "%((fixesschema+'.'+fixestable),variable, variable))
        conn.commit()
        
        cursor.close()
        
    else: print'Invalid argument for method!'

    cursor.close()
    
def Export(port,DBname,username, password,fixesschema,fixestable,path,postgrespath,formato):
    import psycopg2
    try:
        if formato=='csv':
            conn = psycopg2.connect("host='localhost' port= '%s' dbname='%s' user='%s' password=%s" %(port,DBname,username, password))
            conn.set_isolation_level(0)
            cursor = conn.cursor()
            
            cursor.execute("COPY (SELECT * FROM %s) \n TO '%s' DELIMITER ',' CSV HEADER"%((fixesschema+'.'+fixestable),path))
            conn.commit()
        elif formato =='shp':   
            import os
            os.chdir(postgrespath)
            os.system(('pgsql2shp -f %s -h localhost -u %s -P %s -d %s  "SELECT * FROM %s"'%(path,username,password,DBname, (fixesschema+'.'+fixestable))))
        
        else:
            print 'Invalid argument for format'
            
    except(Exception, psycopg2.DatabaseError) as error:
              
            print error        
      
    