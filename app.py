import streamlit as st

from config import NORMALIZATION_RANGES
from input_utils import get_user_inputs
from model_loader import download_model_from_azure
from prediction import prepare_input_data, make_prediction

st.set_page_config(page_title="Apartment Price Predictor", layout="wide")
st.title("Apartment Price Prediction App")

model = download_model_from_azure()

inputs = get_user_inputs()

st.header("Price Prediction")

if st.button("Predict Price"):
    if model is not None:
        try:
            input_df = prepare_input_data(inputs, NORMALIZATION_RANGES)

            with st.expander("Debug: See Model Input"):
                st.dataframe(input_df)

            prediction = make_prediction(model, input_df)

            st.subheader("Predicted Apartment Price:")
            price_str = f"<h1 style='text-align: center; color: #2E86C1;'>{int(prediction):,} PLN</h1>"
            st.markdown(price_str, unsafe_allow_html=True)

            st.subheader("Predicted Price per Square Meter:")
            price_per_m2 = prediction / inputs['squareMeters']
            price_per_m2_str = f"<h2 style='text-align: center; color: #28B463;'>{int(price_per_m2):,} PLN/m²</h2>"
            st.markdown(price_per_m2_str, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")
            st.exception(e)
    else:
        st.error("Model is not loaded. Cannot make a prediction.")
