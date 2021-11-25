# streamlit for web framework
# pandas for data handling and manipulation
# subprocess for descriptor calculation using Java
# os for file handling
# pickle for loading pickle file

import streamlit as st
import pandas as pd
import subprocess
import os
import pickle

# PaDEL descriptor calculator
def desc_calc():
  bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
  process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()
  # SMILES file is not needed after calculation
  os.remove('molecule.smi')

# file download
def filedownload(df):
  csv = df.to_csv(index=False)
  href = f'<a href="data:file/csv;base64,{csv}" download="prediction.csv">Download Predictions</a>'
  return href

# model building
def build_model(input_data):
  # apply loaded model to input data
  load_model = pickle.load(open('sars_cov_proteinase_model.pkl', 'rb'))
  prediction = load_model.predict(input_data)
  # create table for prediction output using 1D arrays
  st.header('**Prediction Output**')
  prediction_output = pd.Series(prediction, name = 'pIC50')
  molecule_name = pd.Series(load_data[1], name = 'Molecule Name')
  df = pd.concat([molecule_name, prediction_output], axis = 1)
  st.write(df)
  # save prediction output table into a file for download using previously created function
  st.markdown(filedownload(df), unsafe_allow_html = True)

# page title
st.markdown("""
# SARS-CoV Bioactivity Prediction App

This app allows you to predict the bioactivity of drug candidates towards inhibiting the SARS coronavirus 3C-like proteinase.

**Credits**
- App built in `Python` and `Streamlit`.
- Methodology provided by [Chanin Nantasenamat](https://medium.com/@chanin.nantasenamat) (aka [Data Professor](http://youtube.com/dataprofessor)).
- Descriptor calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/).
---
""")

# sidebar
with st.sidebar.header('1. Upload your CSV data'):
  uploaded_file = st.sidebar.file_uploader('Upload your file here', type=["csv"])
  st.sidebar.markdown("""
  [Example input file](https://github.com/hamiq/sars_inhibitor_prediction/blob/main/datafiles/
example_sars_drug_bioactivity.csv)
  """)

# when the Predict button is clicked
if st.sidebar.button('Predict'):
  # data file should contain canonical smiles and ChEMBL ID
  load_data = pd.read_table(uploaded_file, sep=",", header=0)
  # save data to SMILE file
  load_data.to_csv('molecule.smi', sep="\t", index=False, header=False)

  st.header('Original Input Data')
  st.write(load_data)

  # calculate descriptors
  with st.spinner('Calculating descriptors...'):
    desc_calc()

  # display calculated descriptors
  st.header('**Calculated Molecular Descriptors**')
  desc = pd.read_csv('descriptors_output.csv')
  st.write(desc)
  st.write(desc.shape)

  # read in descriptor list that does not include the low variance predictors
  st.header('**Subset of Significant Descriptors**')
  Xlist = list(pd.read_csv('descriptor_list.csv').columns)

  # use the column headers of Xlist to filter out the low variance predictors from the current query
  desc_subset = desc[Xlist]
  st.write(desc_subset)
  st.write(desc_subset.shape)

  # apply trained model to make prediction on query
  build_model(desc_subset)

#when the Predict button is not clicked
else:
  st.info('Upload input data in the sidebar to start!')
