import gc
import base64
import re
from time import sleep
import uuid
from array import array

import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats.distributions import chi2
from stqdm import stqdm


def download_button(object_to_download, download_filename, button_text):
    
    # This function has been created as an alternative to streamlit's st.download_button
    # because of bug number 3832 

    object_to_download = object_to_download.to_csv(index=None)
    
    try:
        b64 = base64.b64encode(object_to_download.encode()).decode()
    
    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(19,23, 32);
                color: inherit;
                padding: 0.5rem 0.75rem;
                position: relative;
                text-decoration: none;
                border-radius: 0.25rem;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(250, 250, 250,0.2);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


st.set_page_config(
    page_title="Methylation"
)

with st.sidebar:
    st.header("Template & Instructions")

    st.caption("To get faster results, upload files in CSV format.")

    st.subheader("Gene to be selected File")
    st.write("- The Gene file should contain the names of the genes that need to be selected from the Manifest file and the Data file.")
    st.write("- All Gene names should be written one after the other in a single column. Ensure that NO column header is provided in the file")
    st.write("- All Genes should be mentioned in the correct case as search is case-sensitive.")
    
    st.subheader("Data Files")
    st.write("- Ensure that the data file contains the column TargetID")
    st.write("")
    st.write("")

# Set title
st.title("Welcome!")

# To add particular annotation file

Annot_option = st.selectbox('Select Annotation File',["450K Methylation Manifest file.csv"])
""

# To calculate for selected indices/names
common_file_select = st.checkbox('Want to calculate data only for specific GENES ?')

if common_file_select:

    # When the user has clicked on the checkbox to calculate for specific indices
    # Provide 2 options:
    # User can upload a file with the list of selected indices/names (for Multiple)
    # Or enter a particular index or name (for Single) 

    file_common = st.file_uploader("Upload File with Gene Names",type=["csv","excel","xls","xlsx"])
    ""
    manifest_select_down = st.checkbox('Do you want a file containing Manifest data for each gene ?')


st.header("Data File")
data_files= st.file_uploader("Upload your files here !", type=["csv","excel","xlsx"])

# Submit button
submit =st.button("Start Analysis!")
" "
banner=st.empty()

if submit:
    
    found=True
    ManiTaken =False

    mani_df=pd.DataFrame()
    data_df=pd.DataFrame()

    if common_file_select:
        
        if file_common is not None:
            with st.spinner('Getting Genes File....'):
                if file_common.type == 'text/csv':
                    common_df =pd.read_csv(file_common,header=None)
                else:
                    common_df =pd.read_excel(file_common,header=None)

            with st.spinner('Fetching Manifest File'):
                mani_df= pd.read_csv("450K Methylation Manifest file.csv")
                mani_df=mani_df.fillna("")
                ManiTaken=True
            
            l1=len(common_df)
            for i in stqdm(range(l1),desc='Extracting data from Manifest File'):
                rowV=mani_df['UCSC_REFGENE_NAME'].str.contains(common_df.loc[i,0])
                data_df = pd.concat([data_df, mani_df.loc[rowV,['TargetID','UCSC_REFGENE_NAME']]], axis=0)
                sleep(0.0001)

            with st.spinner('Getting you all selected data from Manifest File'):
                data_df=data_df.fillna("")
                mani_df=pd.merge(data_df['TargetID'], mani_df, how = 'left', on = 'TargetID')
                
                if manifest_select_down:
                    selected_gene_btn = download_button(mani_df,'select-gene-manifest.csv',"Download Selected Manifest Data File")
                    st.markdown(selected_gene_btn, unsafe_allow_html=True)
                
                del common_df
                gc.collect()
            
    
    if data_files is not None:

        if ManiTaken is False:
            with st.spinner('Fetching Manifest File'):
                    mani_df= pd.read_csv("450K Methylation Manifest file.csv")
                    mani_df=mani_df.fillna("")
                    ManiTaken=True

        mani_df=mani_df["TargetID"]

        common_df=pd.DataFrame()
        data_df =pd.DataFrame()

        with st.spinner(f'Reading {data_files.name} File....'):
            if data_files.type == 'text/csv':
                common_df =pd.read_csv(data_files)
            else:
                common_df =pd.read_excel(data_files)
        with st.spinner(f'Getting you all selected data from {data_files.name}'):
            data_df=pd.merge(mani_df, common_df, how = 'left', on = 'TargetID')
            data_df=data_df.fillna("")
            selected_df_btn = download_button(data_df,'data.csv',f"Download {data_files.name} Selected File")  
            st.markdown(selected_df_btn, unsafe_allow_html=True)

    banner=st.success("All Done!")


    


