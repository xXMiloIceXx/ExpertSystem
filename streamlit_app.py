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
    q7 = st.radio("Are there tests running?", ["Yes", "No"], index=None)
    if q7:
        st.session_state.answers['test'] = q7
        st.button("⬅️ Back", on_click=prev_step)
        st.success("All symptoms recorded. You can now run the diagnosis.")

# ======================================
# Diagnosis Execution (Only on Last Page)
# ======================================
if st.session_state.step == 7:
    if st.button("Start Diagnosis", use_container_width=True):
        ans = st.session_state.answers
        env.reset()

        # Assert facts based on stored session answers
        env.assert_string(f"(power-on {ans['power'].lower()})")
        env.assert_string(f"(beeps {ans['beeps'].lower()})")

        if ans['screen'] == "Black/Blank":
            env.assert_string("(screen-black yes)")
        else:
            env.assert_string("(screen-black no)")

        env.assert_string(f"(sudden-shutdown {'yes' if ans['shutdown'] else 'no'})")
        env.assert_string(f"(error-boot-device {'yes' if ans['boot_error'] else 'no'})")
        env.assert_string(f"(time-reset {'yes' if ans['time_reset'] else 'no'})")

        env.run()

        # ======================================
        # Diagnosis Output
        # ======================================
        st.subheader("🛠️ Expert Recommendation")
        diagnoses = [f['message'] for f in env.facts() if f.template.name == "diagnosis"]
        
        if diagnoses:
            for msg in set(diagnoses):
                st.success(f"**Recommended Action:** {msg}")
        else:
            notify_developer(ans)

        # ======================================
        # Reasoning Explanation
        # ======================================
        st.info(
            "Inference Mechanism: Forward chaining was applied. "
            "The system matched asserted facts against IF–THEN rules "
            "to derive possible hardware fault diagnoses."
        )

        
        

        # ======================================
        # VALIDATION & EVALUATION
        # ======================================
        st.write("### 🔍 Validation Summary")
        
        # Pull the stored data from session state
        ans = st.session_state.answers
        
        # Display the summary of what the user selected across all pages
        st.write(f"Inputs → Power: {ans.get('power')}, Beeps: {ans.get('beeps')}, "
                 f"Screen: {ans.get('screen')}, Shutdown: {ans.get('shutdown')}, "
                 f"Boot Error: {ans.get('boot_error')}, Time Reset: {ans.get('time_reset')}")

        if not found:
            # Send the complete dictionary to the developer notification function
            notify_developer({
                "Power": ans.get('power'),
                "Beeps": ans.get('beeps'),
                "Screen": ans.get('screen'),
                "Shutdown": ans.get('shutdown'),
                "Boot Error": ans.get('boot_error'),
                "Time Reset": ans.get('time_reset'),
                "Test Mode": ans.get('test')
            })

# ======================================
# System Reset
# ======================================
if st.button("Reset System"):
    for key in ["power", "beeps", "screen", "shutdown"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()