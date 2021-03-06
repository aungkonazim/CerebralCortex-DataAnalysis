# Copyright (c) 2018, MD2K Center of Excellence
# - Akane Sano <akanes@media.mit.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from cerebralcortex.core.data_manager.raw.stream_handler import DataSet
from cerebralcortex.cerebralcortex import CerebralCortex
from cerebralcortex.core.datatypes.datastream import DataStream
from cerebralcortex.core.datatypes.datastream import DataPoint
from datetime import datetime, timedelta
from core.computefeature import ComputeFeatureBase
from core.feature.sleep_duration.SleepDurationPrediction import SleepDurationPredictor
from cerebralcortex.core.util.spark_helper import get_or_create_sc

import argparse
from typing import List
import pprint as pp
import numpy as np
import pdb
import pickle
import uuid
import json
import traceback
import math
import datetime as dt
import sys
import os
#import utils.config
import traceback
import importlib
import syslog
from datetime import datetime, timedelta

from syslog import LOG_ERR

cc_config_path = None
gps_key = None


feature_class_name = 'SocialJetlag'
WORKDAY_STREAM="org.md2k.data_analysis.feature.working_days"
SLEEP_STREAM="org.md2k.data_analysis.feature.sleep"

class SocialJetlag(ComputeFeatureBase):
#    '''
#    Produce feature from these two streams
#    1. org.md2k.data_analysis.feature.working_days
#    2. org.md2k.data_analysis.feature.sleep
#
#    Social jet lag can be quantified by calculating the absolute
#    difference between mid-sleep on workdays (MSW) and midsleep
#    on free days (MSF):    delta MS = |MSF-MSW|
#    
#    Wittmann, M., Dinich, J., Merrow, M., and Roenneberg,
#    T. Social jetlag: misalignment of biological and social
#    time. Chronobiology international 23, 1-2 (2006),497.509.
#
#    '''


	def get_socialjetlag(self, userid: str, date_range:list):
	
#	'''
#       Calculates the social jetlag for entire data between start_date and end_date for specific participant.
#	'''
		streamids_sleep = self.get_latest_stream_id(user_id=userid, stream_name=SLEEP_STREAM)
		streamids_work = self.get_latest_stream_id(user_id=userid, stream_name=WORKDAY_STREAM)

		midsleep_work=[]
		midsleep_nonwork=[]
		midsleep_nonwork_week=[]
		midsleep_work_week=[]
		midsleep_week=[]
		mid_hr_save=[]
		workday_save=[]
		duration_save=[]
		offset=[]
		mid_hr=[]
		socialjetlag_data=[]
#		start_date=start_time.strftime("%Y%m%d")
#		end_date=end_time.strftime("%Y%m%d")
#		date_range=date_range(start_date,end_date)
		date_range=date_range[1:]

		DATE = [datetime.strptime(x,'%Y%m%d') for x in date_range]

		start_time=DATE[0]
		end_time=DATE[-1]
		#print(start_time, end_time)
		for date in DATE:
			mid_hr_save=[]
			workday_save=[]
			duration_save=[]
 
			#print(date, (date-timedelta(days=1)))
			for streamid_sleep in streamids_sleep:
				ds_sleep = self.CC.get_stream(user_id = userid, stream_id = streamid_sleep['identifier'], day=(date-timedelta(days=1)).strftime("%Y%m%d"))

				
				for ds in ds_sleep.data:
					offset=ds.offset

				data_sleep=ds_sleep.data
				data_sleep=list(set(data_sleep))
				#print(data_sleep.offset)
				mid_hr=[]
				for dat in data_sleep:
					#print(dat.start_time)
                			#print(dat.start_time.date())
					sample=dat.sample
                        		#print(sample)
                			#print(sample[0],sample[1],sample[2])
                			#print(type(sample[1]))

					sleep_hr=sample[1].hour+sample[1].minute/60
					wake_hr=sample[2].hour+sample[2].minute/60

					if sample[1].day != sample[2].day:
                                		wake_hr=wake_hr+24

					mid_hr=(sleep_hr+wake_hr)/2

					if mid_hr < 24:
                                		mid_hr=mid_hr+24



					mid_hr_save.append(mid_hr)

			if mid_hr_save:
                		mid_hr=np.max(mid_hr_save)

			for streamid_work in streamids_work:
                		ds_work = self.CC.get_stream(user_id = userid, stream_id = streamid_work['identifier'], day=date.strftime("%Y%m%d"),localtime=True)

                		#print(ds_sleep)
                		#print(ds_work)
                		data_work=ds_work.data
                		data_work=list(set(data_work))


                		#print(mid_hr)
                		for dat in data_work:
                        		#print(dat)
                        		#print(dat.start_time.date())
                        		duration=dat.end_time-dat.start_time
                        		duration_save.append(duration.seconds)
                        		sample=dat.sample
                        		#print(sample, duration)
                        		if "Office" in sample:
                                		#print("work day")
                                		workday_save.append("work")
                                		
                        		else:
                                		workday_save.append("free")
                		if not data_work:
                        		workday_save.append("free")
                        		duration_save.append(0)

			if duration_save:
                		if workday_save:
                        		if mid_hr:
                                		#print(duration_save,workday_save)
                                		if "work" in workday_save[np.argmax(duration_save)]:
                                        		midsleep_work.append(mid_hr)
                                		else:
                                        		midsleep_nonwork.append(mid_hr)

		midsleep_diff=abs(np.mean(midsleep_nonwork)-np.mean(midsleep_work))
		sample = []
		sample.append(midsleep_diff)
		print('datapoint',start_time, end_time, offset, sample)
		temp = DataPoint(start_time, end_time, offset, sample)
		socialjetlag_data.append(temp)

		try:
			input_stream_names = [WORKDAY_STREAM, SLEEP_STREAM]
			input_streams = []
			if len(socialjetlag_data):
				streams = self.CC.get_user_streams(userid)
			if streams:
				for stream_name, stream_metadata in streams.items():
					if stream_name in input_stream_names:
						input_streams.append(stream_metadata)

			self.store_stream(filepath="social_jetlag.json",
                                              input_streams=input_streams,
                                              user_id=userid,
                                              data=socialjetlag_data)
			print('socialjetlag', socialjetlag_data)

		except Exception as e:
			print("Exception:", str(e))
			print(traceback.format_exc())
			self.CC.logging.log('%s finished processing for user_id %s saved %d '
                            'data points' %
                            (self.__class__.__name__, str(userid),
                             len(socialjetlag_data)))

	def process(self, user: str, all_days: list):
#        """
#        lists requried streams needed for computation.
#        :param str user_id: id of user
#        :param List all_days: Input list of days
#        """

		if self.CC is None:
            		return

		if not user:
            		return

		self.get_socialjetlag(user, all_days)
