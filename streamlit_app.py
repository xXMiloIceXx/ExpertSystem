import streamlit as st
import clips

# ======================================
# Rule Base Loading
# ======================================
# Ensures that the expert system knowledge base is loaded correctly
env = clips.Environment()
RULES_LOADED = False

try:
    env.load("rules.clp")
    RULES_LOADED = True
except Exception as e:
    st.error(f"Verification Failed: Unable to load rules.clp\n{e}")

# ======================================
# Unknown Case Handler
# ======================================
def notify_developer(user_inputs):
    """
    Handles unknown or uncovered scenarios.
    Demonstrates system evaluation and maintainability.
    """
    st.warning("⚠️ No diagnosis found for the given symptoms.")
    st.write("This case will be reviewed to improve the knowledge base.")
    st.write(f"**Logged Symptoms:** {user_inputs}")

# ======================================
# User Interface
# ======================================
st.set_page_config(page_title="Hardware Expert System", page_icon="💻")
st.title("💻 Computer Hardware Fault Diagnosis Expert System")
st.markdown("---")

st.info(
    "This rule-based expert system diagnoses common computer hardware faults "
    "using forward-chaining inference based on user-observed symptoms."
)

# ======================================
# Symptom Input Section
# ======================================
st.subheader("Select Observed Symptoms")

col1, col2 = st.columns(2)

with col1:
    power = st.checkbox("Does the PC power on?" )
    beeps = st.checkbox("Are there diagnostic beeps?" )
    
    # new question added
    test = st.checkbox("Are there test?" )
    boot_error = st.checkbox("Do you see a 'No Bootable Device' error?")

with col2:
    screen = st.checkbox("Is there any display on the screen?" )
    shutdown = st.checkbox("PC shuts down unexpectedly?")
    
    # New Question 2
    time_reset = st.checkbox("Does the system time/date reset frequently?")

# ======================================
# Diagnosis Execution
# ======================================
if st.button("Start Diagnosis", use_container_width=True):

    symptoms_selected = [power, beeps, boot_error, screen, shutdown, time_reset]
    
    if not any(symptoms_selected):
        st.warning("⚠️ Please select at least one symptom to proceed.")

    else:
        env.reset()

        # Assert facts based on checkboxes to match rules.clp
        # We convert True/False to 'yes/no' strings for CLIPS [cite: 1, 2]
        env.assert_string(f"(power-on {'yes' if power else 'no'})")
        env.assert_string(f"(beeps {'yes' if beeps else 'no'})")
        
        # In your rules, 'screen-black yes' means there is NO display [cite: 4, 5, 6]
        # So if 'screen' is Checked (True), screen-black is 'no'
        if screen:
            env.assert_string("(screen-black no)")
        else:
            env.assert_string("(screen-black yes)")

        env.assert_string(f"(sudden-shutdown {'yes' if shutdown else 'no'})")
        env.assert_string(f"(error-boot-device {'yes' if boot_error else 'no'})")
        env.assert_string(f"(time-reset {'yes' if time_reset else 'no'})")

        # Run inference engine
        env.run()

        # ======================================
        # Reasoning Explanation
        # ======================================
        st.info(
            "Inference Mechanism: Forward chaining was applied. "
            "The system matched asserted facts against IF–THEN rules "
            "to derive possible hardware fault diagnoses."
        )

        # ======================================
        # Diagnosis Output
        # ======================================
        st.subheader("🛠️ Expert Recommendation")

        # found = False
        # for fact in env.facts():
        #     if fact.template.name == "diagnosis":
        #         st.success(f"**Recommended Action:** {fact['message']}")
        #         break
        
        diagnoses = []
        found_specific_diagnosis = False # New flag
        
        for fact in env.facts():
            if fact.template.name == "diagnosis":
                msg = fact['message']
                # Check if it's a real diagnosis or just the fallback message
                if msg != "This case will be reviewed to improve the knowledge base.":
                    found_specific_diagnosis = True
                diagnoses.append(msg)
        
        if diagnoses:
            for msg in diagnoses:
                # If it's the fallback, use a neutral info box instead of a success box
                if msg == "This case will be reviewed to improve the knowledge base.":
                    st.info(f"ℹ️ {msg}")
                else:
                    st.success(f"**Recommended Action:** {msg}")
        
        # Use our new flag to trigger the developer notification
        found = found_specific_diagnosis

        # ======================================
        # VALIDATION & EVALUATION
        # ======================================
        st.write("### 🔍 Validation Summary")
        st.write(f"Inputs → Power: {power}, Beeps: {beeps}, Screen: {screen}, Shutdown: {shutdown}, Boot Error: {boot_error}, Time Reset: {time_reset}")

        if not found:
            notify_developer({
                "Power": power,
                "Beeps": beeps,
                "Screen": screen,
                "Shutdown": shutdown,
                "Boot Error": boot_error, 
                "Time Reset": time_reset
            })

# ======================================
# System Reset
# ======================================
if st.button("Reset System"):
    for key in ["power", "beeps", "screen", "shutdown"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()