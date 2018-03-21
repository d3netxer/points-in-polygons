import csv

from shapely.geometry import Point, shape
from shapely import speedups
import shapely.vectorized
import numpy as np

from numpy import genfromtxt

import fiona

import boto3
import botocore

import itertools as IT
import multiprocessing as mp

from collections import Counter

import time
import os

speedups.enable()

def do_job(chunk):
	#print chunk
	#print 'entering do_job'
	featuresPerCountry = {}
	miniDict = {}
	for row in chunk:
		#print "printing chunk"
		#print row
		with fiona.collection('Global_LSIB_Polygons_Simplified.shp','r') as input:
			for polygon in input:
				#print shape(polygon['geometry'])
				#print polygon['properties']['COUNTRY_NA']
				point = Point(float(row[4]), float(row[3]))
				if shape(polygon['geometry']).contains(point):
					#print polygon['properties']['COUNTRY_NA'] + ' contains a point!'
					if polygon['properties']['COUNTRY_NA'] in featuresPerCountry:
						#iterate by 1
						miniDict[polygon['properties']['COUNTRY_NA']] += 1
					else:
						#add new key with value of 1
						miniDict[polygon['properties']['COUNTRY_NA']] = 1
					break  #break here to not have to go through every country
	#print 'miniDict'
	#print miniDict
	return miniDict

def write_csv(sumDict):
	with open('test_output1.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile)

		#write header row
		writer.writerow(['country_name','feature_count'])

		with fiona.collection('Global_LSIB_Polygons_Detailed.shp','r') as input:
				for polygon in input:
					if polygon['properties']['COUNTRY_NA'] in sumDict: 
						writer.writerow([polygon['properties']['COUNTRY_NA'],sumDict[polygon['properties']['COUNTRY_NA']]])
					else:
						writer.writerow([polygon['properties']['COUNTRY_NA'],0])

def main(args=None):

	print 'starting script'

	#KEY="practice/practice.csv"
	KEY="2018-03-12/world_features.csv"
	BUCKET_NAME="aws-athena-mapgive-query-results"

	s3 = boto3.resource('s3') 

	# Print out bucket names
	for bucket in s3.buckets.all():
		print(bucket.name)


	try:
		s3.Bucket(BUCKET_NAME).download_file(KEY, 'my_local_csv.csv')
	except botocore.exceptions.ClientError as e:
		if e.response['Error']['Code'] == "404":
			print("The object does not exist.")
		else:
			raise

	print 'finished downloading mapgive features file'

	my_data = genfromtxt('my_local_csv.csv', delimiter=',')

	print 'finished loading my_data'

	#KEY2="Global_LSIB_Polygons_Detailed/"
	BUCKET_NAME2="hiu-data"

	my_bucket = s3.Bucket('hiu-data')

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

	t1=time.time()

	with open('test_my_local_csv_5000.csv', 'r') as f:
			#simple csv reader is supposed to be 2-3x faster than DictReader
			#reader = csv.DictReader(f)
			reader = csv.reader(f)

			#skips first header row
			next(reader)

			#https://stackoverflow.com/questions/31164731/python-chunking-csv-file-multiproccessing
			# num_procs is the number of workers in the pool
			num_procs = mp.cpu_count()
			# chunksize is the number of lines in a chunk
			chunksize = 20

			print 'cpu count'
			print num_procs

			pool = mp.Pool(num_procs)
			results = []

			call_iter = iter(lambda: list(IT.islice(reader, chunksize*num_procs)), [])

			for chunk in call_iter:
				#print 'chunk'
				#print chunk
				chunk = iter(chunk)
				pieces = list(iter(lambda: list(IT.islice(chunk, chunksize)), []))
				result = pool.map(do_job, pieces)
				results.extend(result)

			print 'printing results'
			print(results)

			pool.close()
			pool.join()

			#https://stackoverflow.com/questions/11290092/python-elegantly-merge-dictionaries-with-sum-of-values
			print 'print dict sum'
			sumDict = sum((Counter(dict(x)) for x in results),Counter())
			print 'sumDict'
			print sumDict

			write_csv(sumDict)

			print("Pool time took:",time.time()-t1)


if __name__ == "__main__":
	main()






