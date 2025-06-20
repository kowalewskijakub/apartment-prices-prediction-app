import os
import tempfile

import streamlit as st
from autogluon.tabular import TabularPredictor
from azure.storage.blob import BlobServiceClient


@st.cache_resource
def download_model_from_azure():
    """
    Pobiera i wczytuje model z Azure Blob Storage.

    Returns:
        TabularPredictor: Wczytany model lub None w przypadku błędu.
    """
    try:
        connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = st.secrets["AZURE_CONTAINER_NAME"]
        model_folder = "autogluon"

        temp_dir = tempfile.mkdtemp()
        model_dir = os.path.join(temp_dir, model_folder)
        os.makedirs(model_dir, exist_ok=True)

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        blobs_list = list(container_client.list_blobs(name_starts_with=model_folder))

        for index, blob in enumerate(blobs_list):
            relative_path = blob.name[len(model_folder):].lstrip('/')
            if not relative_path:
                continue

            local_path = os.path.join(model_dir, relative_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            blob_client = container_client.get_blob_client(blob.name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())

        model = TabularPredictor.load(model_dir, require_py_version_match=False, require_version_match=False)
        st.success("Model successfully loaded from Azure Storage!")
        return model
    except Exception as e:
        st.error(f"Error downloading model: {str(e)}")
        return None
