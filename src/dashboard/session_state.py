import streamlit as st

from dashboard.simulation_controller import (
    SimulationController,
)


def get_simulation_controller():
    """
    Return the existing simulation controller
    for this Streamlit session.

    If one does not exist, create it.
    """

    if (
        "simulation_controller"
        not in st.session_state
    ):

        st.session_state[
            "simulation_controller"
        ] = (
            SimulationController()
        )

    return st.session_state[
        "simulation_controller"
    ]