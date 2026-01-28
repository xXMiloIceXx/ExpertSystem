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
    "This advanced rule-based expert system diagnoses computer hardware faults "
    "using forward-chaining inference with certainty factors and expert knowledge."
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
st.write(f"### Step {st.session_state.step} of 10")
progress = st.progress(st.session_state.step / 10)

# Question 1: Power Status
if st.session_state.step == 1:
    st.subheader("🔌 Power Status")
    q1 = st.radio("What is the power status of your computer?", 
                  ["Computer powers on normally", "No power at all (no lights, no fans)", "Power lights on but system doesn't boot"], 
                  index=None)
    if q1:
        st.session_state.answers['power_status'] = q1
        st.button("Next ➡️", on_click=next_step)

# Question 2: Display Output
elif st.session_state.step == 2:
    st.subheader("🖥️ Display Output")
    q2 = st.radio("What do you see on your monitor/display?", 
                  ["Normal display with image", "Black screen/no display", "Display with visual artifacts (lines, blocks)", "Distorted or corrupted image"], 
                  index=None)
    if q2:
        st.session_state.answers['display_output'] = q2
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 3: System Beeps
elif st.session_state.step == 3:
    st.subheader("🔊 System Beeps")
    q3 = st.radio("Do you hear any beep patterns when starting the computer?", 
                  ["No beeps", "Very short beep (normal POST)", "Short beeps", "Long beeps", "Continuous beeping", "Repeated long beeps"], 
                  index=None)
    if q3:
        st.session_state.answers['beep_pattern'] = q3
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 4: System Behavior
elif st.session_state.step == 4:
    st.subheader("⚙️ System Behavior")
    q4 = st.radio("How does the system behave during startup?", 
                  ["Boots normally", "Powers on but doesn't boot", "Shuts down unexpectedly", "Shows boot warnings"], 
                  index=None)
    if q4:
        st.session_state.answers['system_behavior'] = q4
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 5: Error Messages
elif st.session_state.step == 5:
    st.subheader("⚠️ Error Messages")
    q5 = st.radio("Do you see any specific error messages?", 
                  ["No error messages", "DISK BOOT FAILURE", "No bootable device", "CPU overheat warning", "SMART warning for hard disk"], 
                  index=None)
    if q5:
        st.session_state.answers['error_messages'] = q5
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 6: Hardware Detection
elif st.session_state.step == 6:
    st.subheader("🎵 Hardware Detection")
    q6 = st.radio("Are there any hardware detection issues?", 
                  ["All hardware detected", "Sound card not detected", "Hard disk not detected", "IDE drive not ready"], 
                  index=None)
    if q6:
        st.session_state.answers['hardware_detection'] = q6
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 7: Fan and Power Components
elif st.session_state.step == 7:
    st.subheader("🌀 Fan and Power Components")
    q7 = st.radio("What is the status of fans and power components?", 
                  ["All fans running normally", "No fans running", "Power light on but no fans", "Fans running but system overheating"], 
                  index=None)
    if q7:
        st.session_state.answers['fan_power'] = q7
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 8: Power Supply Issues
elif st.session_state.step == 8:
    st.subheader("⚡ Power Supply Issues")
    q8 = st.radio("Are there any power-related issues?", 
                  ["Power supply working normally", "Power cable connection problems", "No DC output from PSU", "Electrical outlet issues"], 
                  index=None)
    if q8:
        st.session_state.answers['power_supply'] = q8
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 9: System Settings
elif st.session_state.step == 9:
    st.subheader("⏰ System Settings")
    q9 = st.radio("Do you notice any system setting issues?", 
                  ["All settings normal", "Date/time resets frequently", "BIOS settings lost"], 
                  index=None)
    if q9:
        st.session_state.answers['system_settings'] = q9
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Question 10: Additional Symptoms
elif st.session_state.step == 10:
    st.subheader("🔍 Additional Symptoms")
    q10 = st.radio("How confident are you in your observations?", 
                   ["Very confident (100%)", "Confident (80-90%)", "Somewhat confident (60-70%)", "Not very confident (40-50%)"], 
                   index=None)
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    
    if q10:
        st.session_state.answers['confidence'] = q10
        
        # This button triggers the inference engine
        if st.button("🔍 Start Diagnosis", use_container_width=True):
            # Pull the complete set of stored answers
            ans = st.session_state.answers
            env.reset()
            
            # CRITICAL: Initialize 'found' to False so it exists for the check later
            found = False 

            # Map confidence to certainty factor
            confidence_map = {
                "Very confident (100%)": 1.0,
                "Confident (80-90%)": 0.85,
                "Somewhat confident (60-70%)": 0.65,
                "Not very confident (40-50%)": 0.45
            }
            cf_value = confidence_map.get(ans.get('confidence', 'Confident (80-90%)'), 0.85)

            # Assert symptoms based on user answers with proper template structure
            # Power Status
            if "No power at all" in ans.get('power_status', ''):
                env.assert_string(f"(symptom (name power-lights) (value off) (cf {cf_value}))")
                env.assert_string(f"(symptom (name fan-noise) (value none) (cf {cf_value}))")
            elif "Power lights on but system doesn't boot" in ans.get('power_status', ''):
                env.assert_string(f"(symptom (name power-status) (value on) (cf {cf_value}))")
                env.assert_string(f"(symptom (name system-state) (value on-no-boot) (cf {cf_value}))")
            else:
                env.assert_string(f"(symptom (name power-status) (value on) (cf {cf_value}))")

            # Display Output
            if "Black screen/no display" in ans.get('display_output', ''):
                env.assert_string(f"(symptom (name display-status) (value none) (cf {cf_value}))")
                env.assert_string(f"(symptom (name image-displayed) (value no) (cf {cf_value}))")
            elif "visual artifacts" in ans.get('display_output', ''):
                env.assert_string(f"(symptom (name artifacts) (value lines-or-blocks) (cf {cf_value}))")
                env.assert_string(f"(symptom (name image-symmetry) (value asymmetric-random) (cf {cf_value}))")
            elif "Distorted" in ans.get('display_output', ''):
                env.assert_string(f"(symptom (name screen-image) (value distorted) (cf {cf_value}))")

            # Beep Patterns
            beep_mapping = {
                "Very short beep": "very-short",
                "Short beeps": "short", 
                "Long beeps": "long",
                "Continuous beeping": "continuous",
                "Repeated long beeps": "repeated-long"
            }
            beep_pattern = ans.get('beep_pattern', '')
            if beep_pattern != "No beeps":
                env.assert_string(f"(symptom (name beep-code) (value heard) (cf {cf_value}))")
                for pattern, value in beep_mapping.items():
                    if pattern in beep_pattern:
                        env.assert_string(f"(symptom (name beep-duration) (value {value}) (cf {cf_value}))")
                        env.assert_string(f"(symptom (name beep-pattern) (value {value}) (cf {cf_value}))")

            # System Behavior
            if "doesn't boot" in ans.get('system_behavior', ''):
                env.assert_string(f"(symptom (name system-state) (value on-no-boot) (cf {cf_value}))")
            elif "Shuts down unexpectedly" in ans.get('system_behavior', ''):
                env.assert_string(f"(symptom (name system-state) (value shutdown) (cf {cf_value}))")
            elif "boot warnings" in ans.get('system_behavior', ''):
                env.assert_string(f"(symptom (name boot-warning) (value cpu-overheat) (cf {cf_value}))")

            # Error Messages
            error_mapping = {
                "DISK BOOT FAILURE": "disk-boot-failure",
                "CPU overheat warning": "cpu-overheat", 
                "SMART warning": "warning"
            }
            error_msg = ans.get('error_messages', '')
            for error, value in error_mapping.items():
                if error in error_msg:
                    if "SMART" in error:
                        env.assert_string(f"(symptom (name hdd-smart) (value {value}) (cf {cf_value}))")
                    elif "DISK BOOT" in error:
                        env.assert_string(f"(symptom (name error-message) (value {value}) (cf {cf_value}))")
                    elif "CPU overheat" in error:
                        env.assert_string(f"(symptom (name boot-warning) (value {value}) (cf {cf_value}))")

            # Hardware Detection
            if "Sound card not detected" in ans.get('hardware_detection', ''):
                env.assert_string(f"(symptom (name sound-card-status) (value not-detected) (cf {cf_value}))")
            elif "IDE drive not ready" in ans.get('hardware_detection', ''):
                env.assert_string(f"(symptom (name hdd-ide-status) (value not-ready) (cf {cf_value}))")

            # Fan and Power
            if "No fans running" in ans.get('fan_power', ''):
                env.assert_string(f"(symptom (name fans-running) (value no) (cf {cf_value}))")
            elif "Power light on but no fans" in ans.get('fan_power', ''):
                env.assert_string(f"(symptom (name power-light) (value on) (cf {cf_value}))")
                env.assert_string(f"(symptom (name fans-running) (value no) (cf {cf_value}))")

            # Power Supply
            if "Power cable connection problems" in ans.get('power_supply', ''):
                env.assert_string(f"(symptom (name psu-cable) (value improper) (cf {cf_value}))")
                env.assert_string(f"(symptom (name mains-voltage) (value stable) (cf {cf_value}))")
            elif "No DC output" in ans.get('power_supply', ''):
                env.assert_string(f"(symptom (name dc-output) (value none) (cf {cf_value}))")
                env.assert_string(f"(symptom (name primary-circuit) (value good) (cf {cf_value}))")
                env.assert_string(f"(symptom (name oscillation) (value none) (cf {cf_value}))")

            # Run the inference engine
            env.run()

            # ======================================
            # Diagnosis Output
            # ======================================
            st.subheader("🛠️ Expert System Diagnosis")
            
            # Check all facts generated by the engine
            diagnoses = []
            for fact in env.facts():
                if fact.template.name == "diagnosis":
                    diagnoses.append({
                        'fault': fact['fault'],
                        'solution': fact['solution'], 
                        'category': fact['category'],
                        'cf': fact['cf']
                    })
                    found = True

            if diagnoses:
                # Sort by certainty factor (highest first)
                diagnoses.sort(key=lambda x: x['cf'], reverse=True)
                
                for i, diag in enumerate(diagnoses):
                    if i == 0:
                        st.success(f"**Primary Diagnosis:** {diag['fault']}")
                    else:
                        st.info(f"**Alternative Diagnosis:** {diag['fault']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Solution:** {diag['solution']}")
                    with col2:
                        st.write(f"**Category:** {diag['category']}")
                        st.write(f"**Certainty:** {diag['cf']:.2f}")
                    st.markdown("---")
            
            # ======================================
            # VALIDATION & EVALUATION
            # ======================================
            st.write("### 🔍 System Analysis")
            
            # Display what was processed
            st.write("**Symptoms Analyzed:**")
            for key, value in ans.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value}")

            if not found:
                notify_developer(ans)
                
            # ======================================
            # External Link Button
            # ======================================
            st.markdown("---")
            st.subheader("📚 Additional Resources")
            
            # You can change this URL to any link you want
            external_url = "https://www.techsupportguru.com/hardware-troubleshooting"
            
            if st.button("🔗 View Hardware Troubleshooting Guide", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0; url={external_url}">', unsafe_allow_html=True)
                st.success("Redirecting to external troubleshooting resources...")
                
            # Alternative approach using link
            st.markdown(f"[🌐 **Hardware Troubleshooting Guide**]({external_url})", unsafe_allow_html=True)

# ======================================
# System Reset
# ======================================
if st.button("🔄 Reset System", use_container_width=True):
    # Clear the wizard progress
    st.session_state.step = 1
    # Clear all stored answers
    st.session_state.answers = {}
    
    # Optional: Clear any old individual session keys if they exist
    for key in ["power_status", "display_output", "beep_pattern", "system_behavior", "error_messages", "hardware_detection", "fan_power", "power_supply", "system_settings", "confidence"]:
        if key in st.session_state:
            del st.session_state[key]
            
    # Refresh the app to show Page 1
    st.rerun()