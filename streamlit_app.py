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

# Question 1
st.markdown("**1. Does the PC power on?**")
power = st.radio(
    label="",
    options=["Yes", "No"],
    index=None,
    key="power",
    horizontal=True
)

# Question 2
st.markdown("**2. Are there diagnostic beeps during startup?**")
beeps = st.radio(
    label="",
    options=["Yes", "No"],
    index=None,
    key="beeps",
    horizontal=True
)

# Question 3
st.markdown("**3. Is there any display on the screen?**")
screen = st.radio(
    label="",
    options=["Visible", "Black/Blank"],
    index=None,
    key="screen",
    horizontal=True
)

# Question 4
st.markdown("**4. Does the PC shut down unexpectedly after powering on?**")
shutdown = st.checkbox(
    "Yes",
    key="shutdown"
)

# Question 5
st.markdown("**5. Do you see a ‘No Bootable Device’ error message?**")
boot_error = st.checkbox(
    "Yes",
    key="boot_error"
)

# Question 6
st.markdown("**6. Does the system time or date reset frequently?**")
time_reset = st.checkbox(
    "Yes",
    key="time_reset"
)

# Question 7
st.markdown("**7. Are there system test failures or abnormal startup behaviour?**")
test = st.radio(
    label="",
    options=["Yes", "No"],
    index=None,
    key="test",
    horizontal=True
)

# ======================================
# Diagnosis Execution
# ======================================
if st.button("Start Diagnosis", use_container_width=True):

    # Input completeness validation
    if power is None or beeps is None or screen is None:
        st.warning("Please answer all questions before running the diagnosis.")
    
    elif not RULES_LOADED:
        st.error("System error: Rule base not loaded.")

    else:
        env.reset()

        # Assert user inputs as facts (Forward Chaining)
        env.assert_string(f"(power-on {power.lower()})")
        env.assert_string(f"(beeps {beeps.lower()})")

        if screen == "Black/Blank":
            env.assert_string("(screen-black yes)")
        else:
            env.assert_string("(screen-black no)")

        if shutdown:
            env.assert_string("(sudden-shutdown yes)")
        else:
            env.assert_string("(sudden-shutdown no)")

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

        found = False
        for fact in env.facts():
            if fact.template.name == "diagnosis":
                st.success(f"**Recommended Action:** {fact['message']}")
                break

        # ======================================
        # VALIDATION & EVALUATION
        # ======================================
        st.write("### 🔍 Validation Summary")
        st.write(f"Inputs → Power: {power}, Beeps: {beeps}, Screen: {screen}, Shutdown: {shutdown}")

        if not found:
            notify_developer({
                "Power": power,
                "Beeps": beeps,
                "Screen": screen,
                "Shutdown": shutdown
            })

# ======================================
# System Reset
# ======================================
if st.button("Reset System"):
    for key in [
        "power", "beeps", "screen", "shutdown",
        "boot_error", "time_reset", "test"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()