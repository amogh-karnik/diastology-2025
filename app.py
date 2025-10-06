import streamlit as st

st.set_page_config(page_title="Diastolic Function Grading", layout="centered")

st.title("LV Diastolic Function Grading & LAP Estimation")

st.markdown("""
This tool follows the ASE/EACVI 2016 algorithm for **diastolic function assessment**.
Enter echo measurements below to classify diastolic dysfunction and LAP.
""")

# Inputs
st.subheader("Echo Parameters")
septal_e = st.number_input("Septal e′ velocity (cm/s)", min_value=0.0, step=0.1)
lateral_e = st.number_input("Lateral e′ velocity (cm/s)", min_value=0.0, step=0.1)
E_A = st.number_input("Mitral E/A ratio", min_value=0.0, step=0.1)
E = st.number_input("Mitral E velocity (cm/s)", min_value=0.0, step=0.1)
septal_Ee = E / septal_e if septal_e > 0 else None
lateral_Ee = E / lateral_e if lateral_e > 0 else None
avg_e = (septal_e + lateral_e) / 2 if septal_e > 0 and lateral_e > 0 else None
avg_Ee = E / avg_e if avg_e and avg_e > 0 else None

TR_velocity = st.number_input("TR velocity (m/s)", min_value=0.0, step=0.1)
#PASP = st.number_input("PASP (mmHg)", min_value=0.0, step=1.0)

# Supplemental parameters
st.subheader("Supplemental Parameters (optional)")
pv_s_d = st.number_input("Pulmonary vein S/D ratio", min_value=0.0, step=0.01)
lars = st.number_input("Lateral atrial reversal duration (% LARS)", min_value=0.0, step=0.1)
lavi = st.number_input("Left atrial volume index (mL/m²)", min_value=0.0, step=0.1)
ivrt = st.number_input("IVRT (ms)", min_value=0.0, step=1.0)

# Logic
def classify():
    abnormal_vars = 0

    # Rule 1: reduced e'
    reduced_e = (septal_e <= 6) or (lateral_e <= 7) or (avg_e is not None and avg_e <= 6.5)

    # Rule 2: increased E/e'
    increased_Ee = (
        (septal_Ee and septal_Ee >= 15) or
        (lateral_Ee and lateral_Ee >= 13) or
        (avg_Ee and avg_Ee >= 14)
    )

    # Rule 3: TR velocity or PASP
    high_TR = TR_velocity >= 2.8 #or PASP >= 35

    if reduced_e: abnormal_vars += 1
    if increased_Ee: abnormal_vars += 1
    if high_TR: abnormal_vars += 1

    # Decision
    if abnormal_vars == 0:
        return "Normal DF, Normal LAP"
    elif reduced_e and not (increased_Ee or high_TR):
        if E_A <= 0.8:
            return "Grade 1 (Impaired relaxation, Normal LAP)"
        else:
            return "Indeterminate — consider exercise echo if symptomatic"
    elif abnormal_vars >= 2 or increased_Ee or high_TR:
        supplemental_positive = (
            (pv_s_d and pv_s_d <= 0.67) or
            (lars and lars <= 18) or
            (lavi and lavi > 34) or
            (ivrt and ivrt <= 70)
        )
        if supplemental_positive or abnormal_vars == 3:
            if E_A < 2:
                return "Grade 2 (Mild/Moderate ↑ LAP)"
            else:
                return "Grade 3 (Marked ↑ LAP)"
        else:
            if supplemental_positive is None:
                return "Grade 1 (Impaired relaxation, Normal LAP)"
            else:
                return "Indeterminate — need supplemental methods"
    else:
        return "Indeterminate"

if st.button("Classify Diastolic Function"):
    result = classify()
    st.success(f"**Result: {result}**")
