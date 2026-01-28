import streamlit as st
import clips

# ======================================
# CertaintyDiag-Bot Expert System
# ======================================

# Rule Base Loading
env = clips.Environment()
RULES_LOADED = False

try:
    env.load("rules.clp")
    RULES_LOADED = True
except Exception as e:
    st.error(f"Verification Failed: Unable to load rules.clp\n{e}")

# ======================================
# Certainty Factor Protocol
# ======================================

def interpret_user_confidence(user_text):
    """Convert user text to certainty factor (-1.0 to 1.0)"""
    user_lower = user_text.lower()
    
    # Definitely (1.0)
    if any(word in user_lower for word in ["yes, absolutely", "definitely", "100%", "certain", "sure"]):
        return 1.0
    # Almost Certainly (0.8-0.9)
    elif any(word in user_lower for word in ["pretty sure", "almost certain", "most likely", "very likely"]):
        return 0.85
    # Probably (0.6-0.7)
    elif any(word in user_lower for word in ["probably", "think so", "seems to be", "likely"]):
        return 0.65
    # Maybe (0.3-0.5)
    elif any(word in user_lower for word in ["maybe", "might be", "possibly", "could be"]):
        return 0.4
    # Unknown (-0.2 to 0.2)
    elif any(word in user_lower for word in ["don't know", "not sure", "hard to tell", "can't check"]):
        return 0.0
    # Default to moderate confidence
    else:
        return 0.7

def interpret_cf_level(cf_value):
    """Convert CF value to human readable interpretation"""
    if cf_value >= 0.9:
        return "Definitely"
    elif cf_value >= 0.8:
        return "Almost Certainly"
    elif cf_value >= 0.6:
        return "Probably"
    elif cf_value >= 0.3:
        return "Maybe"
    elif cf_value >= -0.2:
        return "Unknown"
    elif cf_value >= -0.5:
        return "Maybe Not"
    elif cf_value >= -0.7:
        return "Probably Not"
    elif cf_value >= -0.9:
        return "Almost Certainly Not"
    else:
        return "Definitely Not"

def run_certainty_diagnosis(global_cf):
    """Execute the CertaintyDiag-Bot reasoning engine"""
    env.reset()
    symptoms = st.session_state.symptoms
    confidence = st.session_state.confidence_levels
    
    st.markdown("---")
    st.subheader("🤖 CertaintyDiag-Bot Analysis Results")
    
    # Assert symptoms with proper CF calculations
    
    # Audio System Analysis
    if 'volume_bar' in symptoms and 'sound_output' in symptoms:
        vol_cf = confidence.get('audio', 0.7)
        
        # Rule A1: Missing Audio Driver
        if "moving" in symptoms['volume_bar'] and "No sound" in symptoms['sound_output']:
            env.assert_string(f"(symptom (name volume-bar-moving) (value yes) (cf {vol_cf}))")
            env.assert_string(f"(symptom (name sound-output) (value none) (cf {vol_cf}))")
        
        # Rule A2: Faulty Speaker
        elif "Distorted" in symptoms['sound_output']:
            env.assert_string(f"(symptom (name sound-quality) (value distorted) (cf {vol_cf}))")
    
    # Thermal System Analysis
    if 'temperature' in symptoms and 'performance' in symptoms:
        temp_cf = confidence.get('thermal', 0.7)
        
        # Rule A4: Temperature Threshold
        if "Very hot" in symptoms['temperature']:
            env.assert_string(f"(symptom (name cpu-temp) (value high) (cf {temp_cf}))")
        
        # Rule A5: Imminent Overheating
        elif "warmer rapidly" in symptoms['temperature']:
            env.assert_string(f"(symptom (name temp-pattern) (value rising-rapidly) (cf {temp_cf}))")
        
        # Rule A6: PSU Aging with random shutdowns
        if "Random shutdowns" in symptoms['performance'] and 'system_age' in symptoms:
            age_cf = confidence.get('storage', 0.7)
            if "Over 3 years" in symptoms['system_age']:
                env.assert_string(f"(symptom (name random-shutdowns) (value yes) (cf {temp_cf}))")
                env.assert_string(f"(symptom (name system-age) (value over-3-years) (cf {age_cf}))")
    
    # Power System Analysis
    if 'power_startup' in symptoms and 'fan_behavior' in symptoms:
        power_cf = confidence.get('power', 0.7)
        
        # Rule B3: Dead System
        if "No response" in symptoms['power_startup'] and "No fan noise" in symptoms['fan_behavior']:
            env.assert_string(f"(symptom (name power-lights) (value off) (cf {power_cf}))")
            env.assert_string(f"(symptom (name fan-noise) (value none) (cf {power_cf}))")
        
        # Rule B4: Partial Power
        elif "Lights but no boot" in symptoms['power_startup'] and "No fan noise" in symptoms['fan_behavior']:
            env.assert_string(f"(symptom (name power-light) (value on) (cf {power_cf}))")
            env.assert_string(f"(symptom (name fans-running) (value no) (cf {power_cf}))")
    
    # Display Analysis
    if 'display' in symptoms and 'display_timing' in symptoms:
        display_cf = confidence.get('display', 0.7)
        
        # Rule AB1: Monitor Physical Damage (Consensus)
        if ("Lines, blocks, artifacts" in symptoms['display'] and 
            "Right at power-on" in symptoms['display_timing']):
            env.assert_string(f"(symptom (name power-status) (value on) (cf {display_cf}))")
            env.assert_string(f"(symptom (name screen-artifacts) (value lines-blocks) (cf {display_cf}))")
            env.assert_string(f"(symptom (name artifact-timing) (value at-boot) (cf {display_cf}))")
    
    # Storage Analysis
    if 'boot_behavior' in symptoms:
        storage_cf = confidence.get('storage', 0.7)
        
        # Rule B5: Critical Drive Failure
        if "DISK BOOT FAILURE" in symptoms['boot_behavior']:
            env.assert_string(f"(symptom (name boot-message) (value disk-boot-failure) (cf {storage_cf}))")
        
        # Rule A7: HDD Wear Pattern
        elif "Random reboots" in symptoms['boot_behavior'] and 'system_age' in symptoms:
            if "Over 3 years" in symptoms['system_age']:
                env.assert_string(f"(symptom (name random-reboots) (value yes) (cf {storage_cf}))")
                env.assert_string(f"(symptom (name device-age) (value old) (cf {storage_cf}))")
    
    # Hardware Detection Analysis
    if 'device_detection' in symptoms:
        detect_cf = confidence.get('detection', 0.7)
        
        if "Sound device not found" in symptoms['device_detection']:
            env.assert_string(f"(symptom (name sound-card-status) (value not-detected) (cf {detect_cf}))")
    
    # Beep Analysis
    if 'beep_pattern' in symptoms:
        beep_cf = confidence.get('beeps', 0.7) * global_cf
        
        # Only process if CF is above Unknown threshold
        if beep_cf > 0.2:
            beep_mapping = {
                "One short beep (normal)": "very-short",
                "Multiple short beeps": "short",
                "Long beeps": "long",
                "Continuous beeping": "continuous"
            }
            
            for pattern, value in beep_mapping.items():
                if pattern in symptoms['beep_pattern']:
                    env.assert_string(f"(symptom (name beep-duration) (value {value}) (cf {beep_cf}))")
    
    # Run the inference engine
    env.run()
    
    # ======================================
    # CertaintyDiag-Bot Results Display
    # ======================================
    
    diagnoses = []
    for fact in env.facts():
        if fact.template.name == "diagnosis":
            diagnoses.append({
                'fault': fact['fault'],
                'solution': fact['solution'],
                'category': fact['category'], 
                'cf': float(fact['cf'])
            })
    
    if diagnoses:
        # Sort by certainty factor
        diagnoses.sort(key=lambda x: x['cf'], reverse=True)
        
        st.success("🎯 **Diagnostic Assessment Complete**")
        
        for i, diag in enumerate(diagnoses):
            cf_interpretation = interpret_cf_level(diag['cf'])
            
            # Color coding based on certainty
            if diag['cf'] >= 0.8:
                st.success(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            elif diag['cf'] >= 0.6:
                st.info(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            elif diag['cf'] >= 0.3:
                st.warning(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            else:
                st.error(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            
            # Diagnosis details
            st.write(f"**Suspected Fault:** {diag['fault']}")
            st.write(f"**Evidence Used:** {list(symptoms.keys())}")
            st.write(f"**Reasoning:** Based on hybrid knowledge base analysis with certainty weighting")
            st.write(f"**Recommended Action:** {diag['solution']}")
            st.write(f"**Category:** {diag['category']}")
            
            st.markdown("---")
        
        # Cross-check recommendations
        if diagnoses[0]['cf'] < 0.6:
            st.warning("⚠️ **Certainty Level Below Threshold**")
            st.write("The diagnosis confidence is in the 'Maybe' range. Consider:")
            st.write("• Gathering more specific evidence")
            st.write("• Cross-checking symptoms with alternative approaches")
            st.write("• Professional hardware inspection")
        
    else:
        st.warning("⚠️ **No Diagnosis Found**")
        st.write("The symptom pattern doesn't match known rules in the knowledge base.")
        st.write("**Possible reasons:**")
        st.write("• Symptoms are in the 'Unknown' range (CF -0.2 to 0.2)")
        st.write("• Novel hardware issue not covered in current rules")
        st.write("• Multiple conflicting symptoms")
        
        st.info("**Recommendation:** Consult professional hardware technician for manual diagnosis.")
    
    # Evidence Summary
    st.markdown("### 🔍 Evidence Summary")
    st.write("**User Symptoms & Confidence Levels:**")
    for symptom, value in symptoms.items():
        cf = confidence.get(symptom.split('_')[0], 0.7)
        cf_text = interpret_cf_level(cf)
        st.write(f"• {symptom.replace('_', ' ').title()}: {value} (*{cf_text}: {cf:.2f}*)")
    
    st.write(f"**Global Confidence Modifier:** {global_cf:.2f} ({interpret_cf_level(global_cf)})")
    
    # ======================================
    # External Links & Actions
    # ======================================
    st.markdown("---")
    st.subheader("📚 Additional Resources")
    
    external_url = "https://docs.google.com/forms/d/e/1FAIpQLScGm5kkIxK88AZM_ElaVZDwIUqQgCG_kP7ficPKa9H3T6QAgQ/viewform?usp=publish-editor"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Provide Feedback", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={external_url}">', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 New Diagnosis", on_click=restart_diagnosis, use_container_width=True):
            st.rerun()

def restart_diagnosis():
    st.session_state.step = 1
    st.session_state.symptoms = {}
    st.session_state.confidence_levels = {}

# ======================================
# User Interface
# ======================================
st.set_page_config(page_title="CertaintyDiag-Bot", page_icon="🤖")
st.title("🤖 CertaintyDiag-Bot: Hardware Expert System")
st.markdown("---")

st.info(
    "🔬 **Hybrid Knowledge Base**: Combining modern symptom-based research with legacy component rules\n\n"
    "📊 **Certainty Factor Logic**: Diagnoses based on evidence quality and user confidence\n\n"
    "🎯 **Precision Diagnosis**: Not just True/False, but certainty levels from -1.0 to 1.0"
)

# ======================================
# Safety Protocol Check
# ======================================
st.markdown("### 🚨 Safety Protocol")
safety_check = st.radio("⚠️ **EMERGENCY CHECK**: Do you see smoke, smell burning, or hear sparking?", 
                       ["No emergency signs", "Yes - I see/smell smoke or burning"], 
                       index=0)

if safety_check == "Yes - I see/smell smoke or burning":
    st.error("🚨 **EMERGENCY PROTOCOL ACTIVATED** 🚨")
    st.error("**IMMEDIATE ACTION REQUIRED:**")
    st.error("1. **UNPLUG THE COMPUTER IMMEDIATELY**")
    st.error("2. **MOVE AWAY FROM THE DEVICE**") 
    st.error("3. **DO NOT USE UNTIL PROFESSIONALLY INSPECTED**")
    st.error("**Diagnosis: Severe Electrical Short - Safety Override**")
    st.stop()

st.success("✅ No emergency detected - proceeding with diagnosis")
st.markdown("---")

# ======================================
# CertaintyDiag-Bot Diagnostic Session
# ======================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {}
if 'confidence_levels' not in st.session_state:
    st.session_state.confidence_levels = {}

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# ======================================
# Evidence Gathering with CF Sensing
# ======================================
total_steps = 8
st.write(f"### 🔍 Evidence Gathering - Step {st.session_state.step} of {total_steps}")
progress = st.progress(st.session_state.step / total_steps)

# Step 1: Audio System Assessment
if st.session_state.step == 1:
    st.subheader("🎵 Audio System Assessment")
    
    # Volume Bar Check
    vol_bar = st.radio("When you play audio, does the volume bar/visualizer in your system move?", 
                      ["I can see it moving", "No movement/no bar", "I think it moves", "Not sure/can't check"])
    
    # Sound Output Check  
    sound_out = st.radio("Do you actually hear sound from speakers/headphones?", 
                        ["Yes, clear sound", "No sound at all", "Distorted/scratchy sound", "Not sure"])
    
    if vol_bar and sound_out:
        st.session_state.symptoms['volume_bar'] = vol_bar
        st.session_state.symptoms['sound_output'] = sound_out
        st.session_state.confidence_levels['audio'] = interpret_user_confidence(f"{vol_bar} {sound_out}")
        st.button("Next ➡️", on_click=next_step)

# Step 2: Thermal System Assessment
elif st.session_state.step == 2:
    st.subheader("🌡️ Thermal & CPU Assessment")
    
    temp_check = st.radio("How does your system feel temperature-wise?", 
                         ["Normal temperature", "Very hot to touch", "Getting warmer rapidly", "Can't tell"])
    
    performance = st.radio("How is system performance?", 
                          ["Normal speed", "Slowing down/throttling", "Random shutdowns", "Not sure"])
    
    if temp_check and performance:
        st.session_state.symptoms['temperature'] = temp_check
        st.session_state.symptoms['performance'] = performance
        st.session_state.confidence_levels['thermal'] = interpret_user_confidence(f"{temp_check} {performance}")
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 3: Power & Startup Assessment
elif st.session_state.step == 3:
    st.subheader("⚡ Power & Startup Assessment")
    
    power_status = st.radio("What happens when you press the power button?", 
                           ["System starts normally", "No response at all", "Lights but no boot", "Starts then shuts down"])
    
    fan_noise = st.radio("Do you hear fans spinning when you power on?", 
                        ["Yes, fans spinning", "No fan noise", "Fans start then stop", "Not sure"])
    
    if power_status and fan_noise:
        st.session_state.symptoms['power_startup'] = power_status
        st.session_state.symptoms['fan_behavior'] = fan_noise
        st.session_state.confidence_levels['power'] = interpret_user_confidence(f"{power_status} {fan_noise}")
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 4: Display Assessment
elif st.session_state.step == 4:
    st.subheader("🖥️ Display Assessment")
    
    screen_status = st.radio("What do you see on your screen?", 
                            ["Normal clear display", "Black/no display", "Lines, blocks, artifacts", "Distorted colors"])
    
    timing = st.radio("When do display problems appear?", 
                     ["No problems", "Right at power-on", "After Windows loads", "Randomly"])
    
    if screen_status and timing:
        st.session_state.symptoms['display'] = screen_status  
        st.session_state.symptoms['display_timing'] = timing
        st.session_state.confidence_levels['display'] = interpret_user_confidence(f"{screen_status} {timing}")
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 5: Storage Assessment
elif st.session_state.step == 5:
    st.subheader("💾 Storage Assessment")
    
    boot_behavior = st.radio("How does your system boot?", 
                            ["Boots normally to desktop", "DISK BOOT FAILURE message", "Slow/struggling boot", "Random reboots"])
    
    system_age = st.radio("How old is your computer/storage device?", 
                         ["Less than 1 year", "1-3 years", "Over 3 years old", "Not sure"])
    
    if boot_behavior and system_age:
        st.session_state.symptoms['boot_behavior'] = boot_behavior
        st.session_state.symptoms['system_age'] = system_age  
        st.session_state.confidence_levels['storage'] = interpret_user_confidence(f"{boot_behavior} {system_age}")
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 6: Hardware Detection
elif st.session_state.step == 6:
    st.subheader("🔍 Hardware Detection")
    
    device_recognition = st.radio("Are all your devices being recognized?", 
                                 ["All devices working", "Sound device not found", "Drive not detected", "Multiple devices missing"])
    
    error_messages = st.radio("Do you see any specific error messages?", 
                             ["No error messages", "Audio driver errors", "SMART drive warnings", "POST/BIOS errors"])
    
    if device_recognition and error_messages:
        st.session_state.symptoms['device_detection'] = device_recognition
        st.session_state.symptoms['error_messages'] = error_messages
        st.session_state.confidence_levels['detection'] = interpret_user_confidence(f"{device_recognition} {error_messages}")
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 7: System Beeps & POST
elif st.session_state.step == 7:
    st.subheader("🔊 System Beeps & POST Assessment")
    
    beep_pattern = st.radio("When you start the computer, what beep pattern do you hear?", 
                           ["One short beep (normal)", "No beeps", "Multiple short beeps", "Long beeps", "Continuous beeping"])
    
    boot_sequence = st.radio("How confident are you about the beep pattern?", 
                            ["Very confident - I hear it clearly", "Somewhat confident", "Not very confident", "I can't tell/no speakers"])
    
    if beep_pattern and boot_sequence:
        st.session_state.symptoms['beep_pattern'] = beep_pattern
        st.session_state.confidence_levels['beeps'] = interpret_user_confidence(boot_sequence)
        
        col1, col2 = st.columns(2)
        col1.button("⬅️ Back", on_click=prev_step)
        col2.button("Next ➡️", on_click=next_step)

# Step 8: Final Assessment & Diagnosis
elif st.session_state.step == 8:
    st.subheader("🎯 Final Assessment")
    
    overall_confidence = st.radio("Overall, how confident are you in your observations?", 
                                 ["Very confident in all my answers", "Confident in most answers", "Some uncertainty", "Significant uncertainty"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Back", on_click=prev_step)
    
    if overall_confidence:
        global_cf = interpret_user_confidence(overall_confidence)
        
        if st.button("🤖 **Run CertaintyDiag-Bot Analysis**", use_container_width=True):
            run_certainty_diagnosis(global_cf)

def run_certainty_diagnosis(global_cf):
    """Execute the CertaintyDiag-Bot reasoning engine"""
    env.reset()
    symptoms = st.session_state.symptoms
    confidence = st.session_state.confidence_levels
    
    st.markdown("---")
    st.subheader("🤖 CertaintyDiag-Bot Analysis Results")
    
    # Assert symptoms with proper CF calculations
    
    # Audio System Analysis
    if 'volume_bar' in symptoms and 'sound_output' in symptoms:
        vol_cf = confidence.get('audio', 0.7)
        
        # Rule A1: Missing Audio Driver
        if "moving" in symptoms['volume_bar'] and "No sound" in symptoms['sound_output']:
            env.assert_string(f"(symptom (name volume-bar-moving) (value yes) (cf {vol_cf}))")
            env.assert_string(f"(symptom (name sound-output) (value none) (cf {vol_cf}))")
        
        # Rule A2: Faulty Speaker
        elif "Distorted" in symptoms['sound_output']:
            env.assert_string(f"(symptom (name sound-quality) (value distorted) (cf {vol_cf}))")
    
    # Thermal System Analysis
    if 'temperature' in symptoms and 'performance' in symptoms:
        temp_cf = confidence.get('thermal', 0.7)
        
        # Rule A4: Temperature Threshold
        if "Very hot" in symptoms['temperature']:
            env.assert_string(f"(symptom (name cpu-temp) (value high) (cf {temp_cf}))")
        
        # Rule A5: Imminent Overheating
        elif "warmer rapidly" in symptoms['temperature']:
            env.assert_string(f"(symptom (name temp-pattern) (value rising-rapidly) (cf {temp_cf}))")
        
        # Rule A6: PSU Aging with random shutdowns
        if "Random shutdowns" in symptoms['performance'] and 'system_age' in symptoms:
            age_cf = confidence.get('storage', 0.7)
            if "Over 3 years" in symptoms['system_age']:
                env.assert_string(f"(symptom (name random-shutdowns) (value yes) (cf {temp_cf}))")
                env.assert_string(f"(symptom (name system-age) (value over-3-years) (cf {age_cf}))")
    
    # Power System Analysis
    if 'power_startup' in symptoms and 'fan_behavior' in symptoms:
        power_cf = confidence.get('power', 0.7)
        
        # Rule B3: Dead System
        if "No response" in symptoms['power_startup'] and "No fan noise" in symptoms['fan_behavior']:
            env.assert_string(f"(symptom (name power-lights) (value off) (cf {power_cf}))")
            env.assert_string(f"(symptom (name fan-noise) (value none) (cf {power_cf}))")
        
        # Rule B4: Partial Power
        elif "Lights but no boot" in symptoms['power_startup'] and "No fan noise" in symptoms['fan_behavior']:
            env.assert_string(f"(symptom (name power-light) (value on) (cf {power_cf}))")
            env.assert_string(f"(symptom (name fans-running) (value no) (cf {power_cf}))")
    
    # Display Analysis
    if 'display' in symptoms and 'display_timing' in symptoms:
        display_cf = confidence.get('display', 0.7)
        
        # Rule AB1: Monitor Physical Damage (Consensus)
        if ("Lines, blocks, artifacts" in symptoms['display'] and 
            "Right at power-on" in symptoms['display_timing']):
            env.assert_string(f"(symptom (name power-status) (value on) (cf {display_cf}))")
            env.assert_string(f"(symptom (name screen-artifacts) (value lines-blocks) (cf {display_cf}))")
            env.assert_string(f"(symptom (name artifact-timing) (value at-boot) (cf {display_cf}))")
    
    # Storage Analysis
    if 'boot_behavior' in symptoms:
        storage_cf = confidence.get('storage', 0.7)
        
        # Rule B5: Critical Drive Failure
        if "DISK BOOT FAILURE" in symptoms['boot_behavior']:
            env.assert_string(f"(symptom (name boot-message) (value disk-boot-failure) (cf {storage_cf}))")
        
        # Rule A7: HDD Wear Pattern
        elif "Random reboots" in symptoms['boot_behavior'] and 'system_age' in symptoms:
            if "Over 3 years" in symptoms['system_age']:
                env.assert_string(f"(symptom (name random-reboots) (value yes) (cf {storage_cf}))")
                env.assert_string(f"(symptom (name device-age) (value old) (cf {storage_cf}))")
    
    # Hardware Detection Analysis
    if 'device_detection' in symptoms:
        detect_cf = confidence.get('detection', 0.7)
        
        if "Sound device not found" in symptoms['device_detection']:
            env.assert_string(f"(symptom (name sound-card-status) (value not-detected) (cf {detect_cf}))")
    
    # Beep Analysis
    if 'beep_pattern' in symptoms:
        beep_cf = confidence.get('beeps', 0.7) * global_cf
        
        # Only process if CF is above Unknown threshold
        if beep_cf > 0.2:
            beep_mapping = {
                "One short beep (normal)": "very-short",
                "Multiple short beeps": "short",
                "Long beeps": "long",
                "Continuous beeping": "continuous"
            }
            
            for pattern, value in beep_mapping.items():
                if pattern in symptoms['beep_pattern']:
                    env.assert_string(f"(symptom (name beep-duration) (value {value}) (cf {beep_cf}))")
    
    # Run the inference engine
    env.run()
    
    # ======================================
    # CertaintyDiag-Bot Results Display
    # ======================================
    
    diagnoses = []
    for fact in env.facts():
        if fact.template.name == "diagnosis":
            diagnoses.append({
                'fault': fact['fault'],
                'solution': fact['solution'],
                'category': fact['category'], 
                'cf': float(fact['cf'])
            })
    
    if diagnoses:
        # Sort by certainty factor
        diagnoses.sort(key=lambda x: x['cf'], reverse=True)
        
        st.success("🎯 **Diagnostic Assessment Complete**")
        
        for i, diag in enumerate(diagnoses):
            cf_interpretation = interpret_cf_level(diag['cf'])
            
            # Color coding based on certainty
            if diag['cf'] >= 0.8:
                st.success(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            elif diag['cf'] >= 0.6:
                st.info(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            elif diag['cf'] >= 0.3:
                st.warning(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            else:
                st.error(f"**{cf_interpretation} ({diag['cf']:.2f})**")
            
            # Diagnosis details
            st.write(f"**Suspected Fault:** {diag['fault']}")
            st.write(f"**Evidence Used:** {list(symptoms.keys())}")
            st.write(f"**Reasoning:** Based on hybrid knowledge base analysis with certainty weighting")
            st.write(f"**Recommended Action:** {diag['solution']}")
            st.write(f"**Category:** {diag['category']}")
            
            st.markdown("---")
        
        # Cross-check recommendations
        if diagnoses[0]['cf'] < 0.6:
            st.warning("⚠️ **Certainty Level Below Threshold**")
            st.write("The diagnosis confidence is in the 'Maybe' range. Consider:")
            st.write("• Gathering more specific evidence")
            st.write("• Cross-checking symptoms with alternative approaches")
            st.write("• Professional hardware inspection")
        
    else:
        st.warning("⚠️ **No Diagnosis Found**")
        st.write("The symptom pattern doesn't match known rules in the knowledge base.")
        st.write("**Possible reasons:**")
        st.write("• Symptoms are in the 'Unknown' range (CF -0.2 to 0.2)")
        st.write("• Novel hardware issue not covered in current rules")
        st.write("• Multiple conflicting symptoms")
        
        st.info("**Recommendation:** Consult professional hardware technician for manual diagnosis.")
    
    # Evidence Summary
    st.markdown("### 🔍 Evidence Summary")
    st.write("**User Symptoms & Confidence Levels:**")
    for symptom, value in symptoms.items():
        cf = confidence.get(symptom.split('_')[0], 0.7)
        cf_text = interpret_cf_level(cf)
        st.write(f"• {symptom.replace('_', ' ').title()}: {value} (*{cf_text}: {cf:.2f}*)")
    
    st.write(f"**Global Confidence Modifier:** {global_cf:.2f} ({interpret_cf_level(global_cf)})")
    
    # ======================================
    # External Links & Actions
    # ======================================
    st.markdown("---")
    st.subheader("📚 Additional Resources")
    
    external_url = "https://docs.google.com/forms/d/e/1FAIpQLScGm5kkIxK88AZM_ElaVZDwIUqQgCG_kP7ficPKa9H3T6QAgQ/viewform?usp=publish-editor"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Provide Feedback", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={external_url}">', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 New Diagnosis", on_click=restart_diagnosis, use_container_width=True):
            st.rerun()

# ======================================
# System Reset
# ======================================
st.markdown("---")
if st.button("🔄 Reset CertaintyDiag-Bot", use_container_width=True):
    restart_diagnosis()
    st.rerun()