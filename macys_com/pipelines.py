# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class MacysComPipeline(object):
#     def process_item(self, item, spider):
#         return item

import requests
import time
from scrapy.utils.project import get_project_settings
import sys, os, datetime
import json
from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter

SETTINGS = get_project_settings()

class MacysComPipeline(object):

	def __init__(self):
		self.files = {}
		self.exporters = {}

		self.total_count = 0;

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline


	def spider_opened(self, spider):
		pass

	def process_item(self, item, spider):
		self.total_count += 1
		print 'total count: %s' % self.total_count

		# category = item['category']
		gender = item['gender']

		# file_name = '%s_%s' % (gender, category)
		# file_name = file_name.replace(' ', '_')
		file_name = "result"
		# content = '{\n'
		# for k in item:
		# 	content += "%s: %s," % (k, item[k])
		# content = content[:len(content) - 1]
		# content += '},\n'

		try:
			file = self.files[file_name]
			file.write(',\n')
			self.exporters[file_name].export_item(dict(item))


		except:
			path = './result/'

			file = open(path + '%s.json' % file_name, 'w+b')
			file.write('{\n"products": [\n')
			# file.write(content)
			self.files[file_name] = file
			self.exporters[file_name] = JsonLinesItemExporter(self.files[file_name])
			self.exporters[file_name].start_exporting()

			self.exporters[file_name].export_item(dict(item))

			# file.write(",\n")

		return item


	def spider_closed(self, spider):
		for key in self.files:
			self.exporters[key].finish_exporting()
			file = self.files[key]
			# file.seek(-1, 1)
			file.write("]\n}")
			file.close()