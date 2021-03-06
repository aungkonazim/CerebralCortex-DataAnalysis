# Copyright (c) 2018, MD2K Center of Excellence
# All rights reserved.
# author: Md Azim Ullah
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
import pickle
import core.computefeature
from cerebralcortex.cerebralcortex import CerebralCortex
from cerebralcortex.core.datatypes.datapoint import DataPoint
from typing import List

Fs = 25 #sampling frequency

window_size = 60 #sliding window size

window_offset = 60 #sliding window offset

path_to_model_files = 'core/resources/models/stress_wrist/' #path of storage

rr_interval_identifier = "org.md2k.data_analysis.feature.rr_interval.v1" #identifier for rr_interval stream

activity_identifier = "org.md2k.data_analysis.feature.activity.wrist.accel_only.10_seconds" #identifier for activity

no_of_feature = 14 #number of features the model was trained with




def get_datastream(CC:CerebralCortex,
                   identifier:str,
                   day:str,
                   user_id:str,
                   localtime:bool)->List[DataPoint]:
    stream_ids = CC.get_stream_id(user_id,identifier)
    data = []
    for stream_id in stream_ids:
        temp_data = CC.get_stream(stream_id=stream_id['identifier'],user_id=user_id,day=day,localtime=localtime)
        if len(temp_data.data)>0:
            data.extend(temp_data.data)
    return data

def get_model():
    """
    Retrieves the specific model files from storage

    :return: Model and Scalar
    :rtype: objects
    """
    model = pickle.loads(core.computefeature.get_resource_contents(
        path_to_model_files+'stress_model_final_final.model'))
    scaler = pickle.loads(core.computefeature.get_resource_contents(
        path_to_model_files + 'stress_scaler_final_final.scaler'))
    return model, scaler
