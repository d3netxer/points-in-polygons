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

	d = pd.read_csv("test_usernames.csv", delimiter=",", usecols=["building_or_hwy","lat","lon","user","timestamp"])

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

	# save to csv
	merged_df.to_csv('mapgive_metrics_test4.csv', columns=["country_name","datetime","unique_users","building_count","highway_count"])
	
	print("Processing time took:",time.time()-t1)

if __name__ == "__main__":
	main()

