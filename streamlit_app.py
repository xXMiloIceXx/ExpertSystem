import streamlit as st
import clips
import os

# NLP for Semantic Similarity
try:
    import spacy
    # Load medium English model with word vectors
    nlp = spacy.load("en_core_web_md")
    NLP_AVAILABLE = True
except ImportError:
    nlp = None
    NLP_AVAILABLE = False
    print("⚠️ Spacy not installed. Install with: pip install spacy")
    print("   Then download model: python -m spacy download en_core_web_md")
except OSError:
    nlp = None
    NLP_AVAILABLE = False
    print("⚠️ Spacy model not found. Download with: python -m spacy download en_core_web_md")

# ======================================
# 0. KNOWLEDGE CONFIGURATION
# ======================================

# Feature Weights for Weighted CBR Algorithm
# Higher weight = More diagnostic significance
FEATURE_WEIGHTS = {
    # Hardware Direct Evidence - Highest Priority
    "error-message": 3.0,
    "beep-code": 3.0,
    "beep-duration": 3.0,
    "screen-visuals": 2.5,
    
    # System Behavior - High Priority
    "system-state": 2.0,
    "cpu-temp": 2.0,
    "temp-pattern": 2.0,
    "power-lights": 2.0,
    "fan-status": 2.0,
    "boot-warning": 2.0,
    "hdd-status": 2.0,
    
    # Software/Indirect Evidence - Medium Priority
    "sound-quality": 1.5,
    "sound-output": 1.5,
    "volume-bar": 1.5,
    "volume-behavior": 1.5,
    "sound-card-status": 1.5,
    "system-behavior": 1.5,
    
    # Environmental Factors - Lower Priority
    "device-age": 0.8,
    "system-age": 0.8,
}

# ======================================
# 1. CBR ENGINE (PYTHON / MEMORY)
# ======================================

def get_user_features(user_answers):
    """
    Converts user UI selections into a Set of feature strings.
    Format: {"volume-bar:moving", "sound-output:none", ...}
    """
    features = set()
    for key, (user_selection, mapping) in user_answers.items():
        if user_selection and user_selection in mapping:
            backend_id, confidence = mapping[user_selection]
            # Ignore 'unknown' or low confidence values to keep the vector clean
            if backend_id and backend_id != "unknown" and confidence > 0.2:
                features.add(f"{key}:{backend_id}")
    return features

def render_multiline(text, box_type=None):
    """Render text with auto line breaks at periods (except last one).
    
    Args:
        text: Text to render
        box_type: 'success', 'warning', 'info', or None for plain markdown
    """
    if text is None:
        return
    
    # Split by periods but keep them
    parts = text.split('. ')
    if len(parts) > 1:
        # Add period back and line break to all except last
        formatted = '\n\n'.join(f"{part}." if i < len(parts) - 1 else part 
                                     for i, part in enumerate(parts))
    else:
        formatted = text.replace("\n", "<br>")
    
    if box_type == 'success':
        st.success(formatted)
    elif box_type == 'warning':
        st.warning(formatted)
    elif box_type == 'info':
        st.info(formatted)
    else:
        st.markdown(formatted, unsafe_allow_html=True)

def run_cbr_analysis(user_features):
    """
    [CBR ENGINE - Enhanced with Weighted Jaccard + Verification Status]
    Reads the text file -> Calculates Weighted Jaccard Similarity -> Returns Best Match.
    Math: Weighted Intersection / Weighted Union
    
    Key Improvements:
    1. Features with higher diagnostic significance contribute more
    2. VERIFIED cases get full score, PENDING cases get 50% penalty
    3. Quality control prevents knowledge pollution
    """
    best_match = None
    max_score = 0.0
    
    # If no library exists, return empty
    if not os.path.exists("case_library.txt"):
        return None, 0.0

    with open("case_library.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Expected Format: CASE-ID | STATUS | features... | Solution [| feedback_score]
            try:
                parts = line.split("|")
                if len(parts) < 4: 
                    # Legacy format support (old cases without status)
                    if len(parts) == 3:
                        case_id = parts[0].strip()
                        status = "VERIFIED"  # Assume legacy cases are verified
                        case_features_str = parts[1].strip()
                        solution = parts[2].strip()
                        feedback_score = 0
                    else:
                        continue
                else:
                    case_id = parts[0].strip()
                    status = parts[1].strip()
                    case_features_str = parts[2].strip()
                    solution = parts[3].strip()
                    feedback_score = int(parts[4].strip()) if len(parts) > 4 else 0
                
                # 🛡️ QUALITY CONTROL: Skip cases with negative feedback
                if feedback_score < -2:
                    continue
                
                # Convert stored case string to Set
                case_features = set(case_features_str.split())
                
                # === ALGORITHM: WEIGHTED JACCARD SIMILARITY ===
                intersection_weight = 0.0
                union_weight = 0.0
                
                all_features = user_features.union(case_features)
                matched_features = user_features.intersection(case_features)
                
                for feature in all_features:
                    # Extract feature type (e.g., "cpu-temp:above-85" -> "cpu-temp")
                    feature_type = feature.split(":")[0] if ":" in feature else feature
                    weight = FEATURE_WEIGHTS.get(feature_type, 1.0)
                    
                    union_weight += weight
                    
                    if feature in matched_features:
                        intersection_weight += weight
                
                if union_weight == 0:
                    score = 0
                else:
                    score = (intersection_weight / union_weight) * 100
                
                # 🆕 VERIFICATION PENALTY: Unverified cases get 50% score reduction
                if status == "PENDING":
                    score *= 0.5
                    
                # Bonus for positive feedback
                if feedback_score > 0:
                    score *= (1 + feedback_score * 0.05)  # +5% per positive vote
                
                # Keep the highest score
                if score > max_score:
                    max_score = score
                    best_match = {
                        "id": case_id,
                        "solution": solution,
                        "matched_features": list(matched_features),
                        "match_quality": "High" if score > 70 else "Medium" if score > 40 else "Low",
                        "status": status,
                        "feedback": feedback_score
                    }
            except Exception as e:
                print(f"Error parsing case line: {line} - {e}")
                continue
                
    return best_match, max_score

def resolve_conflict(rbr_result, rbr_cf, cbr_result, cbr_score):
    """
    [META-REASONING ENGINE]
    Intelligently integrates RBR and CBR results when they conflict.
    
    Decision Strategy:
    1. High RBR confidence (>80%) -> Prefer rule-based diagnosis
    2. High CBR similarity (>70%) + Low RBR confidence -> Prefer case-based diagnosis
    3. Similar confidence levels -> Provide hybrid recommendation
    4. Default -> Prefer RBR (rules are more reliable when confident)
    
    Returns:
        dict: {
            "primary": "rbr" | "cbr" | "hybrid",
            "recommendation": str,
            "reason": str,
            "confidence": float
        }
    """
    rbr_confidence = rbr_cf * 100 if rbr_result else 0
    cbr_confidence = cbr_score if cbr_result else 0
    
    # Strategy 1: High-confidence rule
    if rbr_confidence > 80:
        result = {
            "primary": "rbr",
            "recommendation": rbr_result['solution'],
            "reason": f"Rule-based engine highly confident ({int(rbr_confidence)}%)",
            "confidence": rbr_confidence
        }
        if cbr_result and cbr_confidence > 40:
            result["alternative_solution"] = cbr_result['solution']
            result["alternative_reason"] = f"Historical case match ({int(cbr_confidence)}% similarity)"
            result["alternative_confidence"] = cbr_confidence
        return result
    
    # Strategy 2: Strong case match with weak rule
    elif cbr_confidence > 70 and rbr_confidence < 50:
        return {
            "primary": "cbr",
            "recommendation": cbr_result['solution'],
            "reason": f"Strong match with historical case ({int(cbr_confidence)}% similarity)",
            "confidence": cbr_confidence
        }
    
    # Strategy 3: Both engines have similar confidence
    elif abs(rbr_confidence - cbr_confidence) < 20 and rbr_result and cbr_result:
        # Check if solutions actually differ
        solutions_differ = rbr_result['solution'] != cbr_result['solution']
        
        if solutions_differ:
            reason = (f"🔍 **Comparative Analysis**: Logic engine diagnoses '{rbr_result['fault']}' "
                     f"based on expert rules, while memory bank found a {int(cbr_score)}% similar "
                     f"historical case with different resolution. Both approaches are valid - "
                     f"consider checking hardware connections first.")
        else:
            reason = "Both reasoning engines converge on the same solution with similar confidence"
        
        return {
            "primary": "hybrid",
            "recommendation": f"**Solution A (Logic-Based)**: {rbr_result['solution']}\n\n**Solution B (Case-Based)**: {cbr_result['solution']}",
            "reason": reason,
            "confidence": (rbr_confidence + cbr_confidence) / 2,
            "requires_comparison": solutions_differ
        }
    
    # Strategy 4: Default to RBR
    elif rbr_result:
        return {
            "primary": "rbr",
            "recommendation": rbr_result['solution'],
            "reason": "Rule-based diagnosis (based on domain expert knowledge)",
            "confidence": rbr_confidence
        }
    
    # Fallback: Only CBR available
    elif cbr_result:
        return {
            "primary": "cbr",
            "recommendation": cbr_result['solution'],
            "reason": "Case-based diagnosis only (no matching rules found)",
            "confidence": cbr_confidence
        }
    
    # No results from either engine
    else:
        return {
            "primary": "none",
            "recommendation": "Unable to diagnose - Please consult a technical professional",
            "reason": "Symptom combination does not match any known patterns",
            "confidence": 0
        }

def get_triggered_symptoms(env):
    """
    [EXPLANATION FACILITY]
    Extracts all symptoms that triggered the CLIPS inference.
    Used for explaining WHY a diagnosis was made.
    
    Returns:
        list: [(symptom_name, value, confidence), ...]
    """
    triggered = []
    for fact in env.facts():
        if fact.template.name == "symptom" and fact['cf'] > 0.5:
            triggered.append({
                "name": fact['name'],
                "value": fact['value'],
                "cf": fact['cf']
            })
    return triggered

def get_semantic_endorsement_score(user_solution, rbr_solution):
    """
    [NLP SEMANTIC SIMILARITY]
    Calculates semantic similarity between user-submitted solution and RBR diagnosis.
    Uses Spacy word embeddings to measure semantic distance.
    
    Args:
        user_solution: User-contributed solution text
        rbr_solution: RBR engine's recommended solution
    
    Returns:
        int: Endorsement points (0-50) based on semantic similarity
    
    Scoring:
    - Similarity > 0.85: +50 pts (Highly aligned with expert knowledge)
    - Similarity > 0.65: +30 pts (Semantically related)
    - Similarity > 0.45: +15 pts (Weak correlation)
    - Otherwise: 0 pts
    """
    if not NLP_AVAILABLE or not nlp or not rbr_solution:
        # Fallback to simple string matching if NLP unavailable
        rbr_normalized = rbr_solution.strip().lower()
        user_normalized = user_solution.strip().lower()
        
        if rbr_normalized == user_normalized:
            return 50
        elif any(key_phrase in user_normalized for key_phrase in rbr_normalized.split()[:3]):
            return 25
        return 0
    
    try:
        # Process texts with Spacy
        doc1 = nlp(user_solution.lower())
        doc2 = nlp(rbr_solution.lower())
        
        # Calculate cosine similarity between document vectors
        similarity = doc1.similarity(doc2)
        
        # Convert similarity to endorsement points
        if similarity > 0.85:
            return 50  # Extremely high semantic match
        elif similarity > 0.65:
            return 30  # Strong semantic alignment
        elif similarity > 0.45:
            return 15  # Moderate correlation
        else:
            return 0   # Low semantic similarity
    
    except Exception as e:
        print(f"Error in semantic analysis: {e}")
        return 0

def save_new_case(user_features, correct_solution, is_verified=False):
    """
    [LEARNING ENGINE - Enhanced with Quality Control]
    Saves a new case to the text file with verification status.
    Format: ID | STATUS | feature1 feature2 | Solution | feedback_score
    
    Args:
        user_features: Set of symptom features
        correct_solution: User-provided solution
        is_verified: Whether this is an expert-verified case
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # 🛡️ INPUT VALIDATION
        if not correct_solution or len(correct_solution.strip()) < 10:
            return False, "Solution too brief (minimum 10 characters required)"
        
        # Check for spam patterns
        spam_patterns = ["test", "asdf", "1234", "xxx"]
        if any(pattern in correct_solution.lower() for pattern in spam_patterns):
            return False, "Invalid input detected"
        
        # 1. Generate unique ID
        import time
        case_id = f"CASE-{int(time.time() * 1000) % 100000:05d}"
        
        # 2. Set verification status
        status = "VERIFIED" if is_verified else "PENDING"
        
        # 3. Format features as space-separated string
        feature_str = " ".join(list(user_features))
        
        # 4. Append to file with initial feedback score of 0
        entry = f"{case_id} | {status} | {feature_str} | {correct_solution} | 0\n"
        
        with open("case_library.txt", "a", encoding="utf-8") as f:
            f.write(entry)
        
        if status == "PENDING":
            return True, "✅ Suggestion submitted! It will be reviewed by domain experts."
        else:
            return True, "✅ Verified case added to knowledge base!"
            
    except Exception as e:
        return False, f"Error saving case: {str(e)}"

def check_numerical_convergence(user_features, solution):
    """
    [NUMERICAL CONVERGENCE CHECK]
    Checks if multiple cases with identical symptom combinations exist.
    This indicates pattern stability in the knowledge base.
    
    Returns:
        int: Convergence bonus points (0-40)
    """
    if not os.path.exists("case_library.txt"):
        return 0
    
    matching_cases = 0
    try:
        with open("case_library.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    case_features_str = parts[2].strip()
                    case_features = set(case_features_str.split())
                    
                    # Check if feature sets are identical
                    if user_features == case_features:
                        matching_cases += 1
        
        # Award points based on convergence strength
        if matching_cases >= 3:
            return 40  # Strong pattern detected
        elif matching_cases == 2:
            return 20  # Moderate pattern
        else:
            return 0
    except Exception as e:
        print(f"Error checking convergence: {e}")
        return 0

def check_and_promote_hybrid(case_id, current_score, user_features, solution, rbr_result):
    """
    [MULTI-DIMENSIONAL AUTO-PROMOTION SYSTEM - Enhanced with NLP]
    Promotes cases to VERIFIED based on weighted scoring across multiple criteria.
    
    Scoring System:
    - Community Approval: +20 points per upvote (current_score * 20)
    - NLP Semantic Endorsement: 0-50 points based on similarity with RBR diagnosis
    - Numerical Convergence: +40 points if pattern repeats in knowledge base
    
    Promotion Threshold: 100 points
    
    Args:
        case_id: The case identifier
        current_score: Current community feedback score (net upvotes)
        user_features: Set of symptom features for this case
        solution: The proposed solution
        rbr_result: Current RBR engine diagnosis result
    
    Returns:
        tuple: (should_promote: bool, total_points: int, breakdown: dict)
    """
    breakdown = {
        "community": 0,
        "nlp_endorsement": 0,
        "convergence": 0,
        "semantic_score": 0.0  # For display purposes
    }
    
    # Criterion 1: Community Approval (20 points per upvote)
    community_points = current_score * 20
    breakdown["community"] = community_points
    
    # Criterion 2: NLP Semantic Endorsement (0-50 points)
    # Uses Spacy to measure semantic similarity with expert system diagnosis
    if rbr_result and rbr_result.get('solution'):
        nlp_points = get_semantic_endorsement_score(
            solution, 
            rbr_result['solution']
        )
        breakdown["nlp_endorsement"] = nlp_points
        
        # Calculate semantic similarity percentage for display
        if NLP_AVAILABLE and nlp:
            try:
                doc1 = nlp(solution.lower())
                doc2 = nlp(rbr_result['solution'].lower())
                breakdown["semantic_score"] = round(doc1.similarity(doc2) * 100, 1)
            except:
                breakdown["semantic_score"] = 0.0
    
    # Criterion 3: Numerical Convergence (0-40 points)
    # Check if similar symptom patterns exist in knowledge base
    convergence_points = check_numerical_convergence(user_features, solution)
    breakdown["convergence"] = convergence_points
    
    # Calculate total score
    total_points = sum([v for k, v in breakdown.items() if k != "semantic_score"])
    
    # Promotion threshold: 100 points
    should_promote = total_points >= 100
    
    return should_promote, total_points, breakdown

def update_case_feedback(case_id, vote, user_features=None, rbr_result=None):
    """
    [FEEDBACK SYSTEM - Enhanced with Multi-Dimensional Scoring]
    Updates the feedback score and evaluates auto-promotion using hybrid criteria.
    
    Args:
        case_id: The case identifier
        vote: +1 for helpful, -1 for not helpful
        user_features: Set of symptom features (for convergence check)
        rbr_result: Current RBR diagnosis result (for endorsement check)
    
    Returns:
        tuple: (success: bool, promoted: bool, details: dict)
    """
    try:
        if not os.path.exists("case_library.txt"):
            return False, False, {}
        
        # Read all cases
        with open("case_library.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Update the matching case
        updated = False
        promoted = False
        promotion_details = {}
        
        for i, line in enumerate(lines):
            if line.startswith(case_id):
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    status = parts[1].strip()
                    case_features_str = parts[2].strip()
                    current_solution = parts[3].strip()
                    current_score = int(parts[4].strip()) if len(parts) > 4 else 0
                    
                    # Update vote score
                    new_score = current_score + vote
                    
                    # 🆕 MULTI-DIMENSIONAL AUTO-PROMOTION
                    if status == "PENDING":
                        # Parse features for convergence check
                        if user_features is None and case_features_str:
                            user_features = set(case_features_str.split())
                        
                        # Run hybrid promotion check
                        should_promote, total_points, breakdown = check_and_promote_hybrid(
                            case_id, 
                            new_score, 
                            user_features, 
                            current_solution, 
                            rbr_result
                        )
                        
                        if should_promote:
                            status = "VERIFIED"
                            promoted = True
                            promotion_details = {
                                "total_points": total_points,
                                "breakdown": breakdown,
                                "case_id": case_id
                            }
                            
                            # Detailed logging
                            print(f"✅ AUTO-PROMOTION: Case {case_id} elevated to VERIFIED")
                            print(f"   Total Points: {total_points}/100")
                            print(f"   - Community: {breakdown['community']} pts ({new_score} votes × 20)")
                            print(f"   - NLP Semantic Match: {breakdown['nlp_endorsement']} pts (Similarity: {breakdown.get('semantic_score', 0)}%)")
                            print(f"   - Convergence: {breakdown['convergence']} pts")
                    
                    # Reconstruct the line with updated score and status
                    lines[i] = f"{parts[0].strip()} | {status} | {parts[2].strip()} | {current_solution} | {new_score}\n"
                    updated = True
                    break
        
        if updated:
            # Write back to file
            with open("case_library.txt", "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True, promoted, promotion_details
        return False, False, {}
        
    except Exception as e:
        print(f"Error updating feedback: {e}")
        return False, False, {}

# ======================================
# 2. RBR HELPER (CLIPS / LOGIC)
# ======================================

def assert_fact_with_mapping(env, symptom_name, user_input, mapping_dict):
    """
    Translates User Choice -> CLIPS Fact
    """
    if not user_input or user_input not in mapping_dict:
        return

    # Unpack: (CLIPS Value, Confidence Score)
    clips_value, cf_score = mapping_dict[user_input]

    # Ignore Unknowns to prevent bad logic
    if cf_score <= 0.2:
        return

    # Assert to CLIPS environment
    fact_str = f"(symptom (name {symptom_name}) (value {clips_value}) (cf {cf_score}))"
    env.assert_string(fact_str)

# Initialize CLIPS
env = clips.Environment()
try:
    env.load("rules.clp")
except Exception as e:
    st.error(f"⚠️ Error loading rules.clp: {e}")

# ======================================
# 3. UI CONFIGURATION
# ======================================
st.set_page_config(page_title="Hardware Expert System", page_icon="🧠")
st.title("🧠 Hybrid Expert System (RBR + CBR)")
st.markdown("### Powered by CLIPS (Logic) & Python (Memory)")

if 'step' not in st.session_state: st.session_state.step = 1
if 'answers' not in st.session_state: st.session_state.answers = {}

# ======================================
# 3. DIAGNOSTIC WIZARD
# ======================================
st.markdown("---")
st.write(f"**Step {st.session_state.step} of 6**")
progress = st.progress(st.session_state.step / 6)

# ------------------------------------------------------------------
# STEP 1: VISUAL & DISPLAY
# ------------------------------------------------------------------
if st.session_state.step == 1:
    st.subheader("🖥️ Display & Visuals")
    
    st.caption("Reference: Kiray & Sianturi (2020), Qurashi et al. (2017)")
    # 

    # Mapping logic for Display Rules
    display_mapping = {
        "Lines, black blocks, or artifacts":     ("artifacts", 1.0),
        "Distorted / Corrupted image":           ("distorted", 1.0),
        "Completely black screen":               ("black", 1.0),
        "Normal clear display":                  ("clear", 1.0),
        "Not sure":                              ("unknown", 0.0)
    }
    ans_disp = st.radio("What do you see on the screen?", list(display_mapping.keys()))
    
    if st.button("Next ➡️"):
        st.session_state.answers['screen-visuals'] = (ans_disp, display_mapping)
        st.session_state.step += 1
        st.rerun()

# ------------------------------------------------------------------
# STEP 2: AUDIO SYSTEM
# ------------------------------------------------------------------
elif st.session_state.step == 2:
    st.subheader("🔊 Audio System")
    st.caption("Reference: Jern et al. (2021), Bassil (2012)")
    # 

    # Q1: Volume Bar (Source A)
    vol_mapping = {
        "Green bar is moving":           ("moving", 1.0),
        "Bar moves irregularly/randomly": ("irregular", 1.0),
        "Bar is frozen/gray":            ("frozen", 1.0),
        "Not sure":                      ("unknown", 0.0)
    }
    ans_vol = st.radio("Check Volume Mixer. Is the bar moving?", list(vol_mapping.keys()))
    
    # Q2: Sound Output (Source A)
    sound_mapping = {
        "No sound at all":               ("none", 1.0),
        "Scratchy, distorted, rattling": ("distorted", 1.0),
        "Sound is normal":               ("normal", 1.0)
    }
    ans_sound = st.radio("What do you hear?", list(sound_mapping.keys()))

    # Q3: Hardware Detection (Source B)
    card_mapping = {
        "Sound card NOT detected / Red X": ("not-detected", 1.0),
        "Sound card is detected":          ("detected", 1.0),
        "I can't check this":              ("unknown", 0.0)
    }
    ans_card = st.radio("Is the Sound Card detected in Device Manager?", list(card_mapping.keys()))

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back"): st.session_state.step -= 1; st.rerun()
    if col2.button("Next ➡️"):
        st.session_state.answers['volume-bar'] = (ans_vol, vol_mapping)
        st.session_state.answers['volume-behavior'] = (ans_vol, vol_mapping) # For interference rule
        st.session_state.answers['sound-output'] = (ans_sound, sound_mapping)
        st.session_state.answers['sound-quality'] = (ans_sound, sound_mapping)
        st.session_state.answers['sound-card-status'] = (ans_card, card_mapping)
        st.session_state.step += 1
        st.rerun()

# ------------------------------------------------------------------
# STEP 3: THERMAL & CPU
# ------------------------------------------------------------------
elif st.session_state.step == 3:
    st.subheader("🌡️ Thermal & CPU")
    st.caption("Reference: Chinnathampy et al. (2025), Miracle (2024)")
    
    # Q1: Temperature (Source A)
    temp_mapping = {
        "Above 85°C (Measured)":         ("above-85", 1.0),
        "Rising rapidly/Unusual":        ("rising-rapidly", 0.8),
        "Hot to the touch":              ("above-85", 0.6), # Lower confidence
        "Normal":                        ("normal", 1.0),
        "Not sure":                      ("unknown", 0.0)
    }
    ans_temp = st.radio("CPU Temperature Status:", list(temp_mapping.keys()))

    # Q2: Boot Warning (Source B)
    boot_warn_mapping = {
        "Yes, 'CPU Overheat' warning":   ("cpu-overheat", 1.0),
        "No warning":                    ("none", 1.0)
    }
    ans_warn = st.radio("Did you see a CPU Overheat warning at boot?", list(boot_warn_mapping.keys()))

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back"): st.session_state.step -= 1; st.rerun()
    if col2.button("Next ➡️"):
        st.session_state.answers['cpu-temp'] = (ans_temp, temp_mapping)
        st.session_state.answers['temp-pattern'] = (ans_temp, temp_mapping)
        st.session_state.answers['boot-warning'] = (ans_warn, boot_warn_mapping)
        st.session_state.step += 1
        st.rerun()

# ------------------------------------------------------------------
# STEP 4: POWER & STARTUP (Source B Heavy)
# ------------------------------------------------------------------
elif st.session_state.step == 4:
    st.subheader("⚡ Power & Startup")
    st.caption("Reference: Miracle (2024), Laksana (2024)")
    # 

    # Q1: Lights
    light_mapping = {
        "Lights are ON":       ("on", 1.0),
        "No lights (OFF)":     ("off", 1.0),
        "Not sure":            ("unknown", 0.0)
    }
    ans_light = st.radio("Power LED Status:", list(light_mapping.keys()))
    
    # Q2: Fans
    fan_mapping = {
        "Silent (No noise)":   ("silent", 1.0),
        "Spinning / Noisy":    ("spinning", 1.0),
        "Not sure":            ("unknown", 0.0)
    }
    ans_fan = st.radio("Fan Status:", list(fan_mapping.keys()))

    # Q3: System State (For Laksana rules)
    state_mapping = {
        "Computer is On but Black Screen (No Boot)": ("on-no-boot", 1.0),
        "Computer shuts down randomly":              ("random-shutdowns", 1.0), # For PSU aging
        "Completely dead":                           ("shutdown", 1.0),
        "Boots normally":                            ("booted", 1.0)
    }
    ans_state = st.radio("System Behavior:", list(state_mapping.keys()))

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back"): st.session_state.step -= 1; st.rerun()
    if col2.button("Next ➡️"):
        st.session_state.answers['power-lights'] = (ans_light, light_mapping)
        st.session_state.answers['fan-status'] = (ans_fan, fan_mapping)
        st.session_state.answers['system-state'] = (ans_state, state_mapping)
        st.session_state.answers['system-behavior'] = (ans_state, state_mapping)
        st.session_state.step += 1
        st.rerun()

# ------------------------------------------------------------------
# STEP 5: STORAGE & BEEPS & MESSAGES
# ------------------------------------------------------------------
elif st.session_state.step == 5:
    st.subheader("💾 Storage, Beeps & Errors")
    st.caption("Reference: Bassil (2012), Jern et al. (2021)")

    # Q1: Error Messages (Source A & B)
    err_mapping = {
        "DISK BOOT FAILURE":             ("disk-boot-failure", 1.0),
        "SMART Warning / Backup":        ("smart-warning", 1.0),
        "IDE Drive Not Ready":           ("ide-not-ready", 1.0),
        "No specific error":             ("none", 1.0)
    }
    ans_err = st.radio("Do you see any text errors?", list(err_mapping.keys()))

    # Q2: Beep Codes (Source B)
    # 
    beep_mapping = {
        "One very short beep":           ("very-short", 1.0),
        "One short beep":                ("short", 1.0),
        "Long beeps":                    ("long", 1.0),
        "Repeated long beeps":           ("repeated-long", 1.0),
        "Continuous tone":               ("continuous", 1.0),
        "No beeps":                      ("none", 1.0)
    }
    ans_beep = st.radio("Beep Code Pattern:", list(beep_mapping.keys()))

    # Q3: Age (Source A)
    age_mapping = {
        "Old (> 3 years)":               ("old", 1.0),
        "New (< 3 years)":               ("new", 1.0)
    }
    ans_age = st.radio("Device Age:", list(age_mapping.keys()))

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back"): st.session_state.step -= 1; st.rerun()
    if col2.button("Next ➡️"):
        st.session_state.answers['error-message'] = (ans_err, err_mapping)
        st.session_state.answers['hdd-status'] = (ans_err, err_mapping) # reuse mapping
        st.session_state.answers['beep-duration'] = (ans_beep, beep_mapping)
        st.session_state.answers['beep-code'] = (ans_beep, beep_mapping)
        st.session_state.answers['system-age'] = (ans_age, age_mapping)
        st.session_state.answers['device-age'] = (ans_age, age_mapping)
        st.session_state.answers['boot-behavior'] = (ans_age, age_mapping) # placeholder, mapped in step 4 actually
        st.session_state.step += 1
        st.rerun()

# ======================================
# STEP 6: DUAL-ENGINE DIAGNOSIS
# ======================================
elif st.session_state.step == 6:
    st.subheader("📋 Final Diagnostic Report")

    # State Management
    if "diagnosis_complete" not in st.session_state:
        st.session_state.diagnosis_complete = False

    # 1. Run Button
    if not st.session_state.diagnosis_complete:
        st.info("System Ready. Click to run Hybrid Analysis.")
        if st.button("🚀 Run Diagnosis", use_container_width=True):
            st.session_state.diagnosis_complete = True
            st.rerun()

    # 2. Results Display
    if st.session_state.diagnosis_complete:
        
        # --- A. PREPARE DATA ---
        # Convert UI answers to Feature Set for Python CBR
        user_features = get_user_features(st.session_state.answers)
        
        # --- B. ENGINE 1: CLIPS (Logic/RBR) ---
        env.reset()
        # Convert UI answers to CLIPS Facts
        for symptom_name, (user_selection, mapping) in st.session_state.answers.items():
            assert_fact_with_mapping(env, symptom_name, user_selection, mapping)
        
        env.run()
        
        # Harvest CLIPS Results
        rbr_result = None
        rbr_cf = 0
        rbr_diagnoses = []
        for fact in env.facts():
            if fact.template.name == "diagnosis":
                rbr_diagnoses.append(fact)

        if rbr_diagnoses:
            rbr_diagnoses.sort(key=lambda d: d['cf'], reverse=True)
            rbr_result = rbr_diagnoses[0]
            rbr_cf = rbr_result['cf']
            rbr_alternatives = rbr_diagnoses[1:7]
        else:
            rbr_alternatives = []
        
        # --- C. ENGINE 2: PYTHON (Memory/CBR) ---
        cbr_result, cbr_score = run_cbr_analysis(user_features)

        # --- D. META-REASONING & INTEGRATED RESULTS ---
        resolution = resolve_conflict(rbr_result, rbr_cf, cbr_result, cbr_score)
        
        # 🆕 TOP-LEVEL: FINAL RECOMMENDATION (Most Intuitive)
        if resolution['primary'] == "hybrid" and resolution.get('requires_comparison', False):
            st.warning("⚠️ Diagnostic Conflict Detected - Multiple valid solutions identified")
        elif resolution['primary'] == "none":
            st.error("❌ Unable to provide reliable diagnosis")
        else:
            st.success("✅ Diagnosis Complete")
        
        st.markdown(f"### 🎯 Final Recommendation")
        with st.container():
            render_multiline(resolution['recommendation'], box_type='success')
        
        if resolution.get("alternative_solution"):
            st.markdown("#### 🧭 Alternative Solution (Case-Based)")
            with st.container():
                render_multiline(resolution["alternative_solution"], box_type='warning')
            if resolution.get("alternative_reason"):
                st.caption(resolution["alternative_reason"])
        
        # Confidence metric
        if resolution['confidence'] > 0:
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("System Confidence", f"{int(resolution['confidence'])}%")
            with col_metric2:
                quality = "High" if resolution['confidence'] > 70 else "Medium" if resolution['confidence'] > 40 else "Low"
                st.metric("Reliability", quality)
        
        st.caption(f"**Decision Rationale**: {resolution['reason']}")
        
        # 🆕 TABBED INTERFACE: Separate Intuitive vs Technical Details
        st.markdown("---")
        
        # Show NLP status
        if NLP_AVAILABLE:
            st.info("🧠 NLP Semantic Analysis: **Active** (Spacy en_core_web_md loaded)")
        else:
            st.warning("⚠️ NLP Disabled: Install Spacy for semantic similarity matching")
            with st.expander("📥 How to enable NLP"):
                st.code("pip install spacy", language="bash")
                st.code("python -m spacy download en_core_web_md", language="bash")
                st.caption("Restart the application after installation.")
        
        tab1, tab2, tab3 = st.tabs(["💡 Diagnostic Basis", "⚙️ Inference Details", "📚 Similar Cases"])
        
        with tab1:
            st.subheader("Rule-Based Expert Analysis")
            if rbr_result:
                conf_pct = int(rbr_result['cf'] * 100)
                color = "green" if conf_pct > 70 else "orange"
                
                with st.container():
                    st.markdown(f"**Identified Issue**: :{color}[{rbr_result['fault']}]")
                    st.success(f"**Recommended Action**:\n\n{rbr_result['solution']}")
                    st.write(f"**Diagnosis Category**: {rbr_result['category']}")
                    st.write(f"**Reference**: {rbr_result['citation']}")
                
                st.progress(conf_pct / 100)
                st.caption(f"Rule Confidence: {conf_pct}%")

                if rbr_alternatives:
                    st.markdown("#### 🧩 Alternative Analyses")
                    for alt in rbr_alternatives:
                        alt_conf = int(alt['cf'] * 100)
                        alt_color = "green" if alt_conf > 70 else "orange"
                        with st.expander(f"{alt['fault']} — {alt_conf}%", expanded=False):
                            st.markdown(f"**Identified Issue**: :{alt_color}[{alt['fault']}]")
                            st.warning(f"**Recommended Action**:\n\n{alt['solution']}")
                            st.write(f"**Diagnosis Category**: {alt['category']}")
                            st.write(f"**Reference**: {alt['citation']}")
            else:
                st.warning("No specific expert rule matched this symptom combination.")
        
        with tab2:
            st.subheader("Inference Chain Analysis")
            if rbr_result:
                triggered_symptoms = get_triggered_symptoms(env)
                if triggered_symptoms:
                    st.write("**Symptoms that triggered this diagnosis**:")
                    
                    # Create a dataframe for better visualization
                    import pandas as pd
                    symptom_data = [{
                        "Symptom": s['name'],
                        "Value": s['value'],
                        "Confidence": f"{int(s['cf']*100)}%"
                    } for s in triggered_symptoms]
                    
                    st.dataframe(symptom_data, use_container_width=True)
                    st.caption("ℹ️ These are the facts asserted to the CLIPS inference engine")
                else:
                    st.caption("No explicit symptom triggers recorded")
            else:
                st.info("No rule-based inference was performed.")
        
        with tab3:
            st.subheader("Historical Case Memory")
            if cbr_result and cbr_score > 20:
                quality_color = "green" if cbr_result.get('match_quality') == "High" else "orange" if cbr_result.get('match_quality') == "Medium" else "red"
                
                col_case1, col_case2 = st.columns([2, 1])
                with col_case1:
                    st.write(f"**Case ID**: {cbr_result['id']}")
                    
                    # Format solution with line breaks at periods
                    solution_text = cbr_result['solution']
                    parts = solution_text.split('. ')
                    if len(parts) > 1:
                        formatted_solution = '\n\n'.join(f"{part}." if i < len(parts) - 1 else part 
                                                              for i, part in enumerate(parts))
                        st.info(f"**Solution Applied**:\n\n{formatted_solution}", icon="💡")
                    else:
                        st.info(f"**Solution Applied**: {solution_text}", icon="💡")
                    
                    # Show verification status
                    status = cbr_result.get('status', 'VERIFIED')
                    if status == "VERIFIED":
                        st.success("✓ Expert-verified case")
                    else:
                        st.warning("⏳ User-contributed (pending verification)")
                
                with col_case2:
                    st.metric("Similarity", f"{int(cbr_score)}%")
                    st.metric("Quality", cbr_result.get('match_quality', 'N/A'))
                
                st.progress(cbr_score / 100)
                
                with st.expander("📊 Feature Matching Details"):
                    st.write(f"**Matched {len(cbr_result['matched_features'])} features**:")
                    for feature in cbr_result['matched_features']:
                        feature_type = feature.split(":")[0] if ":" in feature else feature
                        weight = FEATURE_WEIGHTS.get(feature_type, 1.0)
                        st.markdown(f"- `{feature}` (Weight: {weight})")
                
                # 🆕 FEEDBACK MECHANISM
                st.markdown("---")
                st.write("**Was this historical case helpful?**")
                
                # Initialize vote tracking in session state
                if 'voted_cases' not in st.session_state:
                    st.session_state.voted_cases = set()
                
                # Check if user already voted on this case
                already_voted = cbr_result['id'] in st.session_state.voted_cases
                
                col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 3])
                
                with col_fb1:
                    if st.button("👍 Helpful", key="thumbs_up", disabled=already_voted):
                        # Pass user features and RBR result for multi-dimensional scoring
                        success, promoted, details = update_case_feedback(
                            cbr_result['id'], 
                            +1, 
                            user_features,  # For convergence check
                            rbr_result      # For NLP semantic endorsement
                        )
                        if success:
                            # Mark as voted
                            st.session_state.voted_cases.add(cbr_result['id'])
                            
                            if promoted:
                                st.balloons()
                                st.success("🎉 Case Auto-Promoted to VERIFIED!")
                                # Show detailed promotion breakdown
                                with st.expander("📊 Promotion Details", expanded=True):
                                    st.write(f"**Total Score**: {details.get('total_points', 0)}/100 points")
                                    breakdown = details.get('breakdown', {})
                                    
                                    st.metric("Community Votes", f"{breakdown.get('community', 0)} pts")
                                    
                                    nlp_score = breakdown.get('nlp_endorsement', 0)
                                    semantic_pct = breakdown.get('semantic_score', 0)
                                    if NLP_AVAILABLE:
                                        st.metric(
                                            "NLP Semantic Match", 
                                            f"{nlp_score} pts",
                                            delta=f"{semantic_pct}% similarity"
                                        )
                                    else:
                                        st.metric("Text Match", f"{nlp_score} pts")
                                    
                                    st.metric("Pattern Convergence", f"{breakdown.get('convergence', 0)} pts")
                                    
                                    # Trust chain indicator
                                    if nlp_score >= 50:
                                        st.success("🎓 **Expert Validated**: Highly aligned with expert system")
                                    elif breakdown.get('community', 0) >= 100:
                                        st.info("🤝 **Community Choice**: Strong community endorsement")
                                    if breakdown.get('convergence', 0) >= 40:
                                        st.info("📈 **Pattern Recognized**: Recurring solution in knowledge base")
                            else:
                                st.success("✅ Feedback recorded!")
                            st.rerun()
                
                with col_fb2:
                    if st.button("👎 Not Helpful", key="thumbs_down", disabled=already_voted):
                        success, promoted, details = update_case_feedback(
                            cbr_result['id'], 
                            -1, 
                            user_features,
                            rbr_result
                        )
                        if success:
                            st.session_state.voted_cases.add(cbr_result['id'])
                            st.warning("⚠️ Feedback recorded. This case will be reviewed.")
                            st.rerun()
                
                if already_voted:
                    with col_fb3:
                        st.caption("✓ You have already voted on this case")
                
                # Show current feedback score if available
                if cbr_result.get('feedback', 0) != 0:
                    with col_fb3:
                        fb_score = cbr_result.get('feedback', 0)
                        fb_text = f"Community Rating: {fb_score:+d}"
                        if fb_score > 0:
                            st.success(fb_text)
                        else:
                            st.error(fb_text)
            else:
                st.info("No similar historical cases found in the knowledge base.")
                st.caption("This appears to be a unique symptom combination.")

        # --- E. LEARNING MODULE (CBR RETAIN PHASE) ---
        st.markdown("---")
        st.subheader("🎓 Knowledge Acquisition (Adaptive Learning)")
        st.write("**Help improve the system**: If the diagnosis was incorrect or incomplete, share your solution.")
        st.caption("📖 CBR Retain Phase - Enables incremental learning (Aamodt & Plaza, 1994)")
        
        # Expert mode toggle (hidden feature)
        if 'expert_mode' not in st.session_state:
            st.session_state.expert_mode = False
        
        with st.expander("🔧 Advanced Options"):
            expert_password = st.text_input("Expert Mode (Password)", type="password", key="expert_pw")
            if expert_password == "expert123":  # Simple password - replace with proper auth in production
                st.session_state.expert_mode = True
                st.success("✅ Expert mode activated - your submissions will be marked as VERIFIED")
        
        with st.form("learning_form"):
            new_solution = st.text_area(
                "Correct Solution:", 
                placeholder="e.g., Replaced the faulty RAM module in slot 2 with a new 8GB DDR4 stick. System boots normally after replacement.",
                help="Minimum 10 characters. Please be specific and detailed.",
                height=100
            )
            
            col_submit1, col_submit2 = st.columns([1, 2])
            with col_submit1:
                submitted = st.form_submit_button("💾 Submit Solution", use_container_width=True)
            with col_submit2:
                st.caption("🛡️ Your input will be reviewed before becoming part of the knowledge base.")
            
            if submitted:
                if new_solution:
                    success, message = save_new_case(user_features, new_solution, st.session_state.expert_mode)
                    if success:
                        st.success(message)
                        if not st.session_state.expert_mode:
                            st.info("💡 Tip: High-quality contributions may be promoted to verified status by domain experts.")
                    else:
                        st.error(f"❌ Submission failed: {message}")
                else:
                    st.warning("⚠️ Please provide a solution before submitting.")
                
    # Reset
    st.markdown("---")
    if st.button("🔄 Start Over"):
        st.session_state.step = 1
        st.session_state.answers = {}
        if "diagnosis_complete" in st.session_state:
            del st.session_state.diagnosis_complete
        st.rerun()