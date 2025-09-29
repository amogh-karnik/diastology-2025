import streamlit as st

st.set_page_config(page_title="Diastolic Function Grading", layout="centered")

st.title("LV Diastolic Function Grading & LAP Estimation")

st.markdown("""
This tool follows the **ASE/EACVI 2025 updated algorithm** for **diastolic function assessment**.  
Enter echo measurements below to classify diastolic dysfunction and LAP.
""")

# Inputs
st.subheader("Patient Information")
age = st.number_input("Age (years)", min_value=1, max_value=120, step=1)

st.subheader("Echo Parameters")
septal_e = st.number_input("Septal e′ velocity (cm/s)", min_value=0.0, step=0.1)
lateral_e = st.number_input("Lateral e′ velocity (cm/s)", min_value=0.0, step=0.1)
E = st.number_input("Mitral E velocity (cm/s)", min_value=0.0, step=0.1)
A = st.number_input("Mitral A velocity (cm/s)", min_value=0.0, step=0.1)
E_A = E / A if A > 0 else None

septal_Ee = E / septal_e if septal_e > 0 else None
lateral_Ee = E / lateral_e if lateral_e > 0 else None
avg_e = (septal_e + lateral_e) / 2 if septal_e > 0 and lateral_e > 0 else None
avg_Ee = E / avg_e if avg_e and avg_e > 0 else None

TR_velocity = st.number_input("TR velocity (m/s)", min_value=0.0, step=0.1)

# Supplemental parameters
st.subheader("Supplemental Parameters (optional)")
lavi = st.number_input("Left atrial volume index (mL/m²)", min_value=0.0, step=0.1)
lars = st.number_input("Lateral atrial reservoir strain (% LARS)", min_value=0.0, step=0.1)
pv_s_d = st.number_input("Pulmonary vein S/D ratio", min_value=0.0, step=0.01)
ivrt = st.number_input("IVRT (ms)", min_value=0.0, step=1.0)


def classify():
    abnormal_vars = 0

    # --- Age-adjusted cutoffs for e′ (ASE/EACVI 2025 update) ---
    if age < 40:
        septal_cutoff, lateral_cutoff = 7.0, 10.0
    elif 40 <= age <= 65:
        septal_cutoff, lateral_cutoff = 6.0, 8.0
    else:  # >65
        septal_cutoff, lateral_cutoff = 6.0, 7.0

    # Rule 1: reduced e′ (below age-specific cutoff OR avg <= 6.5 cm/s)
    reduced_e = (
        (septal_e > 0 and septal_e <= septal_cutoff) or
        (lateral_e > 0 and lateral_e <= lateral_cutoff) or
        (avg_e is not None and avg_e <= 6.5)
    )

    # Rule 2: increased E/e′
    increased_Ee = (
        (septal_Ee and septal_Ee >= 15) or
        (lateral_Ee and lateral_Ee >= 13) or
        (avg_Ee and avg_Ee >= 14)
    )

    # Rule 3: TR velocity
    high_TR = TR_velocity >= 2.8

    if reduced_e: abnormal_vars += 1
    if increased_Ee: abnormal_vars += 1
    if high_TR: abnormal_vars += 1

    # --- Decision Tree (ASE/EACVI 2025 update) ---
    if abnormal_vars == 0:
        return "Normal DF, Normal LAP"

    elif reduced_e and not (increased_Ee or high_TR):
        if E_A <= 0.8:
            return "Grade 1 (Impaired relaxation, Normal LAP); if symptomatic, consider Diastolic Exercise Echo"
        else:
            # Check supplemental + abnormal burden
            supplemental_positive = (
                (pv_s_d > 0 and pv_s_d <= 0.67) or
                (lars > 0 and lars <= 18) or
                (lavi > 0 and lavi >= 34) or
                (ivrt > 0 and ivrt <= 70)
            )
            if supplemental_positive or abnormal_vars >= 2:
                if E_A < 2:
                    return "Grade 2 (Mild/Moderate ↑ LAP)"
                else:
                    return "Grade 3 (Marked ↑ LAP)"
            else:
                return "Indeterminate — need supplemental methods"

    else:
        # If abnormal_vars ≥2 but not falling neatly in above branch
        supplemental_positive = (
            (pv_s_d > 0 and pv_s_d <= 0.67) or
            (lars > 0 and lars <= 18) or
            (lavi > 0 and lavi >= 34) or
            (ivrt > 0 and ivrt <= 70)
        )
        if supplemental_positive or abnormal_vars == 3:
            if E_A < 2:
                return "Grade 2 (Mild/Moderate ↑ LAP)"
            else:
                return "Grade 3 (Marked ↑ LAP)"
        else:
            return "Indeterminate — need supplemental methods"


if st.button("Classify Diastolic Function"):
    result = classify()
    st.success(f"**Result: {result}**")
