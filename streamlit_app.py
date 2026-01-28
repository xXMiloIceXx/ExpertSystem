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
# Page State Management
# ======================================
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'answers' not in st.session_state:
    st.session_state.answers = {}

def next_page():
    st.session_state.page += 1

def restart():
    st.session_state.page = 1
    st.session_state.answers = {}

# ======================================
# Multi-Page Question Flow
# ======================================
st.subheader(f"Step {st.session_state.page} of 7")

if st.session_state.page == 1:
    q1 = st.radio("1. Does the PC power on?", ["Yes", "No"], index=None)
    if q1:
        st.session_state.answers['power'] = q1
        st.button("Next", on_click=next_page)

elif st.session_state.page == 2:
    q2 = st.radio("2. Are there diagnostic beeps?", ["Yes", "No"], index=None)
    if q2:
        st.session_state.answers['beeps'] = q2
        st.button("Next", on_click=next_page)

elif st.session_state.page == 3:
    q3 = st.radio("3. Is there any display on the screen?", ["Visible", "Black/Blank"], index=None)
    if q3:
        st.session_state.answers['screen'] = q3
        st.button("Next", on_click=next_page)

elif st.session_state.page == 4:
    q4 = st.checkbox("4. PC shuts down unexpectedly?")
    st.session_state.answers['shutdown'] = q4
    st.button("Next", on_click=next_page)

elif st.session_state.page == 5:
    q5 = st.checkbox("5. Do you see a 'No Bootable Device' error?")
    st.session_state.answers['boot_error'] = q5
    st.button("Next", on_click=next_page)

elif st.session_state.page == 6:
    q6 = st.checkbox("6. Does the system time/date reset frequently?")
    st.session_state.answers['time_reset'] = q6
    st.button("Next", on_click=next_page)

elif st.session_state.page == 7:
    q7 = st.radio("7. Are there test?", ["Yes", "No"], index=None)
    if q7:
        st.session_state.answers['test'] = q7
        # Final Step: Show the Start Diagnosis button
        st.markdown("---")
        st.success("All symptoms recorded. Ready to diagnose.")

# ======================================
# Diagnosis Execution
# ======================================
if st.button("Start Diagnosis", use_container_width=True):

    # Input completeness validation
    if power is None or beeps is None or screen is None:
        st.warning("Please answer all yes/no questions before running the diagnosis.")
    
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
            
        # new inputs
        if test:
            env.assert_string("(sudden-test yes)")
        else:
            env.assert_string("(sudden-test no)")

        if boot_error:
            env.assert_string("(error-boot-device yes)")
        else:
            env.assert_string("(error-boot-device no)")
            
        if time_reset:
            env.assert_string("(time-reset yes)")
        else:
            env.assert_string("(time-reset no)")

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