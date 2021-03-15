from src.AppAvaCal import app_ava_cal
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

T = 100
N = 100
file = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".") \
       + os.sep + 'paperCode' + os.sep + "file.xlsx"
result = app_ava_cal(file, T, N)

# app_info = pd.read_excel(file, sheet_name="Application_info")
# vnf_info = pd.read_excel(file, sheet_name="VNF_info")
# node_info = pd.read_excel(file, sheet_name="node_info")
# edge_info = pd.read_excel(file, sheet_name="edge_info")
# fail_info = pd.read_excel(file, sheet_name = "fail_info")

single_result = result[0]
single_result['mean'] = single_result.apply(np.mean, axis=1)
single_result.to_excel("result.xlsx")