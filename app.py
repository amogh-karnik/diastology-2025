import streamlit as st

st.set_page_config(page_title="Diastolic Function Grading", layout="centered")

st.title("LV Diastolic Function Grading & LAP Estimation")

st.markdown("""
This tool follows the **ASE 2025 updated algorithm** for **diastolic function assessment**.  
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
with st.expander("Show Optional Diastolic Strain/Flow Inputs"):
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
    # Note: Check for 'is not None' is sufficient since min_value=0.0 is set.
    # An e' of 0.0 is highly abnormal and should count as 'reduced'.
    reduced_e = (
        (septal_e is not None and septal_e <= septal_cutoff) or
        (lateral_e is not None and lateral_e <= lateral_cutoff) or
        (avg_e is not None and avg_e <= 6.5)
    )

    # Rule 2: increased E/e′
    increased_Ee = (
        (septal_Ee is not None and septal_Ee >= 15) or
        (lateral_Ee is not None and lateral_Ee >= 13) or
        (avg_Ee is not None and avg_Ee >= 14)
    )

    # Rule 3: TR velocity
    high_TR = TR_velocity is not None and TR_velocity >= 2.8

    if reduced_e: abnormal_vars += 1
    if increased_Ee: abnormal_vars += 1
    if high_TR: abnormal_vars += 1

    # --- Supplemental parameters (optional) ---
    supplemental_positive = (
        (pv_s_d is not None and 0 < pv_s_d <= 0.67) or
        (lars is not None and 0 < lars <= 18) or
        (lavi is not None and lavi >= 34) or
        (ivrt is not None and 0 < ivrt <= 70)
    )

    # --- Decision Tree (ASE/EACVI 2025 update) ---
    if abnormal_vars == 0:
        return "Normal DF, Normal LAP"

    # CASE: Only Rule 1 (reduced e') is positive (Impaired Relaxation Pattern)
    elif reduced_e and not (increased_Ee or high_TR):
        if E_A is not None and E_A <= 0.8:
            return "Grade 1 (Impaired relaxation, Normal LAP); if symptomatic, consider Diastolic Exercise Echo"
        else:
            # E/A > 0.8: Indeterminate or Grade 2/3 (Pseudo-normal)
            if supplemental_positive:
                if E_A is not None and E_A < 2:
                    return "Grade 2 (Mild/Moderate ↑ LAP)"
                elif E_A is not None:
                    return "Grade 3 (Marked ↑ LAP)"
                else:
                    return "Indeterminate — need E/A ratio" # Refinement: must have E/A
            else:
                return "Indeterminate — need supplemental methods"

    # CASE: 1, 2, or 3 abnormal variables (excluding the pure Grade 1 case handled above)
    # This primarily covers scenarios where increased_Ee or high_TR are positive.
    else:
        if abnormal_vars == 3: # 3 abnormal variables is a strong predictor of high LAP
            if E_A is not None and E_A < 2:
                return "Grade 2 (Mild/Moderate ↑ LAP)"
            elif E_A is not None:
                return "Grade 3 (Marked ↑ LAP)"
            else:
                return "Indeterminate — need E/A ratio" # Must have E/A

        elif supplemental_positive:
            # Supplemental data is available to resolve the Indeterminate 1 or 2 abnormal variables
            if E_A is not None and E_A < 2:
                return "Grade 2 (Mild/Moderate ↑ LAP)"
            elif E_A is not None:
                return "Grade 3 (Marked ↑ LAP)"
            else:
                return "Indeterminate — need E/A ratio"
        
        else:
            # Case with 1 or 2 abnormal variables AND NO supplemental data
            return "Indeterminate — need supplemental methods"

if st.button("Classify Diastolic Function"):
    result = classify()
    st.success(f"**Result: {result}**")
