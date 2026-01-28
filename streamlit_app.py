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
# Session State for Wizard Navigation
# ======================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'answers' not in st.session_state:
    st.session_state.answers = {}

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def restart():
    st.session_state.step = 1
    st.session_state.answers = {}

# ======================================
# Question Pages
# ======================================
st.write(f"### Step {st.session_state.step} of 7")
progress = st.progress(st.session_state.step / 7)

# Question 1: Power
if st.session_state.step == 1:
    q1 = st.radio("Does the PC power on?", ["Yes", "No"], index=None)
    if q1:
        st.session_state.answers['power'] = q1
        st.button("Next ➡️", on_click=next_step)

# Question 2: Beeps
elif st.session_state.step == 2:
    q2 = st.radio("Are there diagnostic beeps?", ["Yes", "No"], index=None)
    if q2:
        st.session_state.answers['beeps'] = q2
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 3: Screen
elif st.session_state.step == 3:
    q3 = st.radio("Is there any display on the screen?", ["Visible", "Black/Blank"], index=None)
    if q3:
        st.session_state.answers['screen'] = q3
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 4: Shutdown (Checkbox converted to Yes/No for clarity)
elif st.session_state.step == 4:
    q4 = st.radio("Does the PC shut down unexpectedly?", ["Yes", "No"], index=None)
    if q4:
        st.session_state.answers['shutdown'] = (q4 == "Yes")
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 5: Boot Error
elif st.session_state.step == 5:
    q5 = st.radio("Do you see a 'No Bootable Device' error?", ["Yes", "No"], index=None)
    if q5:
        st.session_state.answers['boot_error'] = (q5 == "Yes")
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 6: Time Reset
elif st.session_state.step == 6:
    q6 = st.radio("Does the system time/date reset frequently?", ["Yes", "No"], index=None)
    if q6:
        st.session_state.answers['time_reset'] = (q6 == "Yes")
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 7: Test Mode
elif st.session_state.step == 7:
    ans_test = st.radio("7. Are there test?", ["Yes", "No"], index=None)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    
    if ans_test:
        st.session_state.answers['test'] = ans_test
        
        # This button triggers the inference engine
        if st.button("Start Diagnosis", use_container_width=True):
            # Pull the complete set of stored answers
            ans = st.session_state.answers
            env.reset()
            
            # CRITICAL: Initialize 'found' to False so it exists for the check later
            found = False 

            # Assert facts based on your knowledge base rules
            env.assert_string(f"(power-on {ans['power'].lower()})")
            env.assert_string(f"(beeps {ans['beeps'].lower()})")

            # Logic mapping for screen status
            if ans['screen'] == "Black/Blank":
                env.assert_string("(screen-black yes)")
            else:
                env.assert_string("(screen-black no)")

            # Mapping checkboxes/radios to yes/no facts
            env.assert_string(f"(sudden-shutdown {'yes' if ans.get('shutdown') else 'no'})")
            env.assert_string(f"(error-boot-device {'yes' if ans.get('boot_error') else 'no'})")
            env.assert_string(f"(time-reset {'yes' if ans.get('time_reset') else 'no'})")

            env.run()

            # ======================================
            # Diagnosis Output
            # ======================================
            st.subheader("🛠️ Expert Recommendation")
            
            # Check all facts generated by the engine
            for fact in env.facts():
                if fact.template.name == "diagnosis":
                    st.success(f"**Recommended Action:** {fact['message']}")
                    found = True # A diagnosis was found

            # ======================================
            # VALIDATION & EVALUATION
            # ======================================
            st.write("### 🔍 Validation Summary")
            
            # Display what was sent to the engine
            st.write(f"Inputs → Power: {ans.get('power')}, Beeps: {ans.get('beeps')}, "
                     f"Screen: {ans.get('screen')}, Shutdown: {ans.get('shutdown')},  "
                     f"Time Reset: {ans.get('time_reset')}, Boot Error: {ans.get('boot_error')}, Test: {ans.get('test')}")

            if not found:
                # This now works because 'found' is defined above as False or True
                notify_developer(ans)

# ======================================
# System Reset
# ======================================
if st.button("Reset System", use_container_width=True):
    # Clear the wizard progress
    st.session_state.step = 1
    # Clear all stored answers
    st.session_state.answers = {}
    
    # Optional: Clear any old individual session keys if they exist
    for key in ["power", "beeps", "screen", "shutdown"]:
        if key in st.session_state:
            del st.session_state[key]
            
    # Refresh the app to show Page 1
    st.rerun()