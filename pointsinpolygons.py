import csv

from shapely.geometry import Point, shape
import shapely.vectorized
import numpy as np
import pandas as pd

from shapely.prepared import prep

#from numpy import genfromtxt

import fiona
import boto3
import botocore

#import itertools as IT
import multiprocessing as mp

#from collections import Counter
import time
import os
from pathlib2 import Path

def main(args=None):

	print 'starting script'


	KEY="2018-03-12/world_features.csv"
	BUCKET_NAME="aws-athena-mapgive-query-results"

	s3 = boto3.resource('s3') 

	#Print out bucket names
	#for bucket in s3.buckets.all():
		#print(bucket.name)

	# don't download file if it exists locally
	my_file1 = Path("/opt/my_local_csv.csv")
	if not my_file1.is_file():

		try:
			s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_csv.csv')
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
			else:
				raise

	print 'finished downloading mapgive features file'

	#KEY2="Global_LSIB_Polygons_Detailed/"
	BUCKET_NAME2="hiu-data"

	my_bucket = s3.Bucket('hiu-lsib')

	my_file2 = Path("/opt/Global_LSIB_Polygons_Detailed.shp")
        if not my_file2.is_file():

		try:
			#s3.Bucket(BUCKET_NAME2).download_file(KEY2, '')
			for object in my_bucket.objects.all():
				print object
				my_bucket.download_file(object.key, object.key)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
			else:
				raise

	print 'finished downloading country polygon file'


	#https://stackoverflow.com/questions/18259393/numpy-loading-csv-too-slow-compared-to-matlab
        #d = pd.read_csv("my_local_csv.csv", delimiter=",", usecols=["building_or_hwy","lat","lon"]).values
	d = pd.read_csv("my_local_csv.csv", delimiter=",", usecols=["building_or_hwy","lat","lon"])

        print 'finished loading points from csv into numpy array'
        print d

        #d = np.delete(d,[0,1,2],axis=1)
	
	highway_d = d[d['building_or_hwy'].str.match('highway')]
        print highway_d

        building_d = d[d['building_or_hwy'].str.match('building')]
        print building_d

	highway_x=highway_d['lon']
	highway_y=highway_d['lat']

	building_x=building_d['lon']
        building_y=building_d['lat']

        #testing a single country
        '''
	x=d[:,1]
        y=d[:,0]
        Uganda_mask2 = shapely.vectorized.contains(Uganda_shp_geom, x, y)
        print 'finished Uganda_mask2'
        print Uganda_mask2
        print 'Uganda_mask2 sum'
        print np.sum(Uganda_mask2)
        '''

	num_procs = mp.cpu_count()	
	print 'cpu count'
	print num_procs
        t1=time.time()

	with open('output.csv', 'wb') as csvfile:
                writer2 = csv.writer(csvfile)
                #write header row
                writer2.writerow(['country_name','building_count','highway_count'])

                with fiona.collection('Global_LSIB_Polygons_Simplified.shp','r') as input:
                        for polygon in input:
                                country_name  = polygon['properties']['COUNTRY_NA']
                                country_shp_geom = shape(polygon['geometry'])
                                print country_name
                                buildings_country_contains = shapely.vectorized.contains(country_shp_geom, building_x, building_y)
				highways_country_contains = shapely.vectorized.contains(country_shp_geom, highway_x, highway_y)
                                buildings_sum_country_contains = np.sum(buildings_country_contains)
				highways_sum_country_contains = np.sum(highways_country_contains)
                                #print buildings_sum_country_contains
                                writer2.writerow([country_name,buildings_sum_country_contains,highways_sum_country_contains])

	print("Processing time took:",time.time()-t1)


if __name__ == "__main__":
	main()






