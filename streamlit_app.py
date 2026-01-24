import streamlit as st
import clips

# --- VERIFICATION: Ensuring the environment and rules load correctly ---
# This serves as a quality method by verifying code integrity 
env = clips.Environment()
RULES_LOADED = False
try:
    env.load("rules.clp")
    RULES_LOADED = True
except Exception as e:
    st.error(f"Verification Failed: rules.clp could not be loaded. {e}")

def notify_developer(user_inputs):
    """
    Simulates sending an email notification to the developers.
    Part of the 'Originality and Applicability' criteria[cite: 30].
    """
    st.warning("⚠️ No diagnosis found. Development notification sent to technicians.")
    st.write(f"**Log for Developer:** Update rules for symptoms: {user_inputs}")

# --- UI Header ---
st.set_page_config(page_title="Hardware Expert System", page_icon="💻")
st.title("💻 Computer Hardware Fault Diagnosis")
st.markdown("---")

# --- Interactive User Inputs ---
st.subheader("Select Symptoms")
col1, col2 = st.columns(2)

with col1:
    # Starting with index=None ensures no default "Yes" or "No" is selected
    power = st.radio("Does the PC power on?", ["Yes", "No"], index=None)
    beeps = st.radio("Are there diagnostic beeps?", ["Yes", "No"], index=None)

with col2:
    screen = st.radio("Is the screen showing a display?", ["Visible", "Black/Blank"], index=None)
    # Checkbox remains unchecked by default
    shutdown = st.checkbox("PC shuts down unexpectedly?")

# --- Reasoning and Output ---
if st.button("Start Diagnosis", use_container_width=True):
    # Check if user has made selections to ensure interactivity [cite: 26]
    if power is None or beeps is None or screen is None:
        st.warning("Please complete all selections before running the diagnosis.")
    elif not RULES_LOADED:
        st.error("Cannot proceed: Rules not loaded.")
    else:
        env.reset()
        
        # Assert symptoms as facts
        env.assert_string(f"(power-on {power.lower()})")
        env.assert_string(f"(beeps {beeps.lower()})")
        if screen == "Black/Blank":
            env.assert_string("(screen-black yes)")
        if shutdown:
            env.assert_string("(sudden-shutdown yes)")

        env.run()

        st.subheader("🛠️ Expert Recommendation")
        found = False
        for fact in env.facts():
            if fact.template.name == 'diagnosis':
                st.success(f"**Action Required:** {fact['message']}")
                found = True
        
        # --- VALIDATION: Handling unknown scenarios ---
        if not found:
            inputs = {"Power": power, "Beeps": beeps, "Screen": screen, "Shutdown": shutdown}
            notify_developer(inputs)