import streamlit as st
import clips

# Initialize CLIPS
env = clips.Environment()
try:
    env.load("rules.clp")
except:
    st.error("Please ensure rules.clp is in the same folder.")

# UI Header - Meets "Professional Overview" requirement
st.set_page_config(page_title="Hardware Expert System", page_icon="💻")
st.title("💻 Computer Hardware Fault Diagnosis")
st.markdown("---")

# Interactive User Inputs
st.subheader("Select Symptoms")
col1, col2 = st.columns(2)

with col1:
    power = st.radio("Does the PC power on?", ["Yes", "No"])
    beeps = st.radio("Are there diagnostic beeps?", ["Yes", "No"])

with col2:
    screen = st.radio("Is the screen showing a display?", ["Visible", "Black/Blank"])
    shutdown = st.checkbox("PC shuts down unexpectedly?")

# Reasoning and Output
if st.button("Start Diagnosis", use_container_width=True):
    env.reset()
    
    # Assert symptoms as facts
    env.assert_string(f"(power-on {power.lower()})")
    env.assert_string(f"(beeps {beeps.lower()})")
    if screen == "Black/Blank":
        env.assert_string("(screen-black yes)")
    if shutdown:
        env.assert_string("(sudden-shutdown yes)")

    env.run()

    # Displaying Results in a User-Friendly Box
    st.subheader("🛠️ Expert Recommendation")
    found = False
    for fact in env.facts():
        if fact.template.name == 'diagnosis':
            st.success(f"**Action Required:** {fact['message']}")
            found = True
    
    if not found:
        st.info("No specific fault detected. Ensure all cables are plugged in correctly.")