import pandas as pd
import streamlit as st


def render_evaluation_view(
    results,
):

    st.header("🧪 AI Model Evaluation")

    if not results:

        st.info("No model evaluation " "results available yet.")

        return

    dataframe = pd.DataFrame(results)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )
