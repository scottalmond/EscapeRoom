"""
   Copyright 2018 Scott Almond

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Purpose:
This class provides wrapper methods for commonly used assets such as 2D images
and 3D models

Usage:

"""

#supporting libraries
import csv #for reading csv config files

class ResourceManager:
	def __init__(self):
		pass

	def clean(self):
		pass
		
	def dispose(self):
		pass

	"""
	given a filename, fetch the contents into an array or dictionaries
	with dictionary keys as the column titles
	ex: [{'key1':'value1','key2':'value2'},{'key1':'value3','key2':'value4'}]
	ref: https://www.reddit.com/r/learnpython/comments/2l07bz/help_reading_csv_file_and_putting_data_into_arrays/
	"""
	@staticmethod
	def loadCSV(filename):
		data=[]
		with open(filename) as file_obj:
			reader = csv.DictReader(file_obj, delimiter=',')
			for row in reader:
				data.append(row)
		return data
				
