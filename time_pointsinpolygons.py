import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import boto3
import botocore

import multiprocessing as mp

import time
import os
from pathlib2 import Path

import sys

def main(args=None):

	num_procs = mp.cpu_count()
	print 'cpu count'
	print num_procs
	t1=time.time()

        BUCKET_NAME="aws-athena-mapgive-query-results"

        s3 = boto3.resource('s3')
        s3_client = boto3.client('s3')
        get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))

        #objs = s3_client.list_objects_v2(Bucket=BUCKET_NAME)['Contents']
        #obj_key_list = [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)]

	paginator = s3_client.get_paginator('list_objects_v2')
	pages = paginator.paginate(Bucket=BUCKET_NAME)

	obj_key_list = []
	for page in pages:
		for obj in page['Contents']:
			obj_key_list.append(obj)

	obj_key_list = [obj['Key'] for obj in sorted(obj_key_list, key=get_last_modified, reverse=True)]

        print('print obj_key_list[0]')
        print(obj_key_list[0])



        #find the first entry in obj_key_list that ends with 'csv'
        
        #get most recent date
        

        most_recent_date = obj_key_list[0].split("/");
        most_recent_date = most_recent_date[0]

        print('most recent date')
        print(most_recent_date)

        KEYS = []

        for name in obj_key_list:
            #print(name)
            if name.endswith('.csv'):
                print(name)
                print('print name split')
                print(name.split("/"))
                if name.split("/")[0] == most_recent_date:
                    KEY = name
                    print(KEY)
                    #break
                    KEYS.append(KEY)


        print('print KEYS')
        print(KEYS)

        #print('print obj_key_list')
        #print(obj_key_list)

        #exit early for testing purposes
        #sys.exit()

        #if testing script, don't download file if it exists locally
        #my_file1 = Path("/opt/my_local_csv.csv")

        #if not my_file1.is_file():

        dataframe_list = []

        for num,KEY in enumerate(KEYS,start=1):
            try:
                 s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_csv.csv')
            except botocore.exceptions.ClientError as e:
                 if e.response['Error']['Code'] == "404":
                     print("The object does not exist.")
                 else:
                     raise

            print("finished downloading mapgive features file {}".format(num))

            print('print KEY')
            print(KEY)

            file_date = KEY.split("/");
            file_date = file_date[0]

            print 'print file_date'
            print file_date
            #sys.exit()

	    d = pd.read_csv("my_local_csv.csv", delimiter=",", usecols=["building_or_hwy","lat","lon","user","timestamp"])

            dataframe_list.append(d)

        for i in dataframe_list:
            print('print dataframe length')
            print(len(i))

        d = pd.concat(dataframe_list)

        print("print combined dataframe list")
        print(len(d))

	# https://gis.stackexchange.com/questions/174159/convert-a-pandas-dataframe-to-a-geodataframe
	geometry = [Point(xy) for xy in zip(d.lon, d.lat)]
	d = d.drop(['lon', 'lat'], axis=1)
	crs = {'init': 'epsg:4326'}
	gd = gpd.GeoDataFrame(d, crs=crs, geometry=geometry)

	countries = gpd.read_file("Global_LSIB_Polygons_Simplified.shp")

	point_with_country = gpd.sjoin(gd,countries, how="inner", op="intersects")

	# point_with_country.head()

	# need to group by month 
	point_with_country['datetime'] = pd.to_datetime(point_with_country['timestamp'])
	point_with_country = point_with_country.set_index('datetime')

	# by country and by month aggregate unique users
	# https://sites.google.com/site/kittipat/programming-with-python/pandasaggregatecountdistinct
	# get sql like output, https://stackoverflow.com/questions/19523277/renaming-column-names-in-pandas-groupby-function/40962126
	# print point_with_country.groupby(['COUNTRY_NA',pd.Grouper(freq="M")]).agg({"user": pd.Series.nunique}).reset_index()
	unique_user_agg = point_with_country.groupby(['COUNTRY_NA',pd.Grouper(freq="M")]).agg({"user": pd.Series.nunique}).reset_index()

	# https://stackoverflow.com/questions/41576242/valueerror-cannot-insert-id-already-exists
	# pivot with grouping months 
	prepivot = point_with_country.groupby(['COUNTRY_NA',pd.Grouper(freq="M"),'building_or_hwy']).agg({"building_or_hwy": pd.Series.count}).rename(columns={'building_or_hwy':'COUNT'}).reset_index()

	# need to pivot using 2 columns
	# https://stackoverflow.com/questions/35414625/pandas-how-to-run-a-pivot-with-a-multi-index
	building_hwy_country_agg = prepivot.pivot_table(index=['COUNTRY_NA','datetime'], columns='building_or_hwy', values='COUNT').reset_index()

	# merge two dataframes 
	merged_df = pd.merge(unique_user_agg, building_hwy_country_agg,  how='outer', on=['COUNTRY_NA','datetime'])

	#replace NaN with 0
	merged_df = merged_df.fillna(0)

	# rename columns
	merged_df = merged_df.rename(index=str, columns={"COUNTRY_NA": "country_name", "user": "unique_users", "building": "building_count", "highway": "highway_count"})


        file_name = '%s-mapgive-metrics.csv' % file_date

        print('file name is:')
        print(file_name)

	# save to csv
	merged_df.to_csv("/opt/data/%s" % file_name, columns=["country_name","datetime","unique_users","building_count","highway_count"])
	
	print("Processing time took:",time.time()-t1)

        KEY="/opt/data/%s" % file_name
        BUCKET_NAME="mapgive-metrics"

        print('printing KEY')
        print KEY

        # don't upload file if it exists
        # my_file2 = Path("/opt/data/mapgive_metrics.csv")
        # my_file2 = Path(KEY)

        # if not my_file2.is_file():

        try:
            s3.Bucket(BUCKET_NAME).upload_file(KEY,file_name)
            object_acl = s3.ObjectAcl('mapgive-metrics',file_name)
            response = object_acl.put(ACL='public-read')     
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
        else:
            print('exception raised')
            #raise

        print 'finished uploading mapgive metrics to s3'

if __name__ == "__main__":
    main()

