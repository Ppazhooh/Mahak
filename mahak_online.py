import argparse
import numpy as np
from modAL.models import ActiveLearner
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import WhiteKernel, RBF
import os
import pandas as pd
import itertools
import sys
from modAL.uncertainty import entropy_sampling
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn import preprocessing
from sklearn.preprocessing import QuantileTransformer
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures
import helper



# Parser
parser = argparse.ArgumentParser(description="Mahak's Parser")

parser.add_argument('-cc', type=str, help='Target Congestion Control Scheme')
parser.add_argument('-budget', type=int, help='Desired Computation Budget')
parser.add_argument('-metric', type=str, help='Target Evaluation Metric.\
                                         For now we support: delay, utilization\
                                         and first power')

parser.add_argument('-buffer', type=str, help='Min, Max and Search Step for \
                                         Buffer Space. Ex: 5,100,2')
parser.add_argument('-mRTT', type=str, help='Min, Max and Search Step for \
                                       mRTT Space. Ex: 5,100,2')
parser.add_argument('-bw', type=str, help='Min, Max and Search Step for \
                                     BW Space. Ex: 5,100,2')
parser.add_argument('-change', type=str, help='Min, Max and Search Step for \
                                         Change Space. Ex: 0.1,4,0.2')

args = parser.parse_args()
cc = args.cc
budget = args.budget
metric = args.metric

buffer_list = args.buffer.split(',')
min_buffer = int(buffer_list[0])
max_buffer = int(buffer_list[1])
buffer_step = int(buffer_list[2])

mRTT_list = args.mRTT.split(',')
min_mRTT = int(mRTT_list[0])
max_mRTT = int(mRTT_list[1])
mRTT_step = int(mRTT_list[2])

bw_list = args.bw.split(',')
min_BW = int(bw_list[0])
max_BW = int(bw_list[1])
bw_step = int(bw_list[2])

change_list = args.change.split(',')
min_step = float(change_list[0])
max_step = float(change_list[1])
change_step = float(change_list[2])

# Create Unlabeled Data Points in the Search Space
buffer_space = list(np.arange(min_buffer, max_buffer + buffer_step, \
                                                                buffer_step))
mRTT_space = list(np.arange(min_mRTT, max_mRTT + mRTT_step, \
                                                                mRTT_step))
bw_space = list(np.arange(min_BW, max_BW + bw_step, bw_step))
change_space = list(np.arange(min_step, max_step + change_step, \
                                                                change_step))
change_space = [ '%.2f' % elem for elem in change_space ]

F = [buffer_space, mRTT_space, bw_space, change_space]
data = []
for element in itertools.product(*F):
    data.append(element)
TrainData = np.array(data)
TrainData = pd.DataFrame(TrainData,
                                columns=["buffer_size","mRTT","BW","bw_step"])


# Train Data Normalization
scaler = MinMaxScaler()
T_data = scaler.fit_transform(TrainData)
pca = PCA()
D_data = pca.fit_transform(T_data)

# Mahak Starts With a Random Choice in Space
n_initial = 1
initial_idx = np.random.choice(range(len(D_data)), size=n_initial)
X_training, y_training = D_data[initial_idx,:],\
     helper.oracle_query(np.array(TrainData.iloc[initial_idx])[0], metric, cc)

# Define the Kernel and the GR
kernel = RBF(length_scale=0.1, length_scale_bounds=(1e-60, 1e5))
regressor = ActiveLearner(
            estimator=GaussianProcessRegressor(kernel=kernel,
            n_restarts_optimizer=10, normalize_y=True, random_state=100),
            query_strategy=helper.GP_regression_std,
             X_training=X_training, y_training=y_training)

# Iterate using Provided Computation Budget
for idx in range(budget):
    query_idx,  query_instance = regressor.query(D_data)
    new_data_original = np.array(TrainData.iloc[query_idx])
    new_data_transformed = D_data[query_idx,:].reshape(1, -1)
    new_label = helper.oracle_query (new_data_original, metric, cc)
    regressor.teach(new_data_transformed, new_label)

# Use the Trained Model to Create the Mapping of the Entire Space
final_result = helper.GP_regression_result(regressor, D_data)

# Create Prediction Dataframe and Saving
TrainData[metric] = final_result
name_to_save = 'predictions/' + 'Mahak_' + cc + '.csv'
TrainData.to_csv(name_to_save)


