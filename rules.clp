;; =========================================================
;; 1. TEMPLATES (Knowledge Representation)
;; =========================================================

;; Template for user observations/symptoms
(deftemplate symptom
   (slot name)                    ;; ID of the symptom (e.g., sound-card-status)
   (slot value)                   ;; Value (e.g., not-detected, heating)
   (slot cf (type FLOAT) (default 1.0))) ;; Certainty Factor of observation (0.0 to 1.0)

;; Template for the final diagnosis
(deftemplate diagnosis
   (slot fault)                   ;; The identified problem
   (slot solution)                ;; The expert solution
   (slot category)                ;; Hardware category
   (slot cf (type FLOAT) (default 0.0))) ;; Calculated Certainty Factor

;; =========================================================
;; 2. RULES (Knowledge Base)
;; =========================================================

;; ---------------------------------------------------------
;; Category: Hard Disk and Audio Faults
;; ---------------------------------------------------------

(defrule audio-card-failure
   ;; IF sound card cannot be detected
   (symptom (name sound-card-status) (value not-detected) (cf ?cf1))
   =>
   ;; THEN Sound card is damaged/not installed
   (assert (diagnosis 
      (fault "Sound Card Damaged or Not Installed") 
      (solution "Replace the Sound Card.") 
      (category "Audio")
      (cf (* ?cf1 0.95))))) ;; High certainty in rule

(defrule hdd-smart-warning
   ;; IF SMART warning is displayed
   (symptom (name hdd-smart) (value warning) (cf ?cf1))
   =>
   ;; THEN Serious mechanical problems
   (assert (diagnosis 
      (fault "Serious Mechanical Hard Disk Failure") 
      (solution "Immediately backup data and replace the drive.") 
      (category "Storage")
      (cf (* ?cf1 1.0)))))

(defrule hdd-ide-delay
   ;; IF HDD (IDE) is not ready during startup
   (symptom (name hdd-ide-status) (value not-ready) (cf ?cf1))
   =>
   ;; THEN Drive not spinning up fast enough
   (assert (diagnosis 
      (fault "Hard Disk Spin-up Latency") 
      (solution "Enable or increase the Hard Disk pre-delay time in BIOS.") 
      (category "Storage")
      (cf (* ?cf1 0.85)))))

;; ---------------------------------------------------------
;; Category: System Startup and Power Issues
;; ---------------------------------------------------------

(defrule dead-system
   ;; IF no signs of power (no lights, no fan)
   (symptom (name power-lights) (value off) (cf ?cf1))
   (symptom (name fan-noise) (value none) (cf ?cf2))
   =>
   (assert (diagnosis 
      (fault "Total Power Failure") 
      (solution "Check power cables, PSU, and electrical outlet.") 
      (category "Power")
      (cf (* (min ?cf1 ?cf2) 0.9)))))

(defrule beep-codes-display
   ;; IF power on BUT no display AND beep codes heard
   (symptom (name power-status) (value on) (cf ?cf1))
   (symptom (name display-status) (value none) (cf ?cf2))
   (symptom (name beep-code) (value heard) (cf ?cf3))
   =>
   (assert (diagnosis 
      (fault "POST Hardware Failure") 
      (solution "Consult beep code guide (RAM, Mobo, or GPU).") 
      (category "Startup")
      (cf (* (min ?cf1 ?cf2 ?cf3) 0.9)))))

(defrule cpu-overheat-boot
   ;; IF CPU overheat warning at boot
   (symptom (name boot-warning) (value cpu-overheat) (cf ?cf1))
   =>
   (assert (diagnosis 
      (fault "CPU Overheating") 
      (solution "Check CPU fan/heatsink and apply new thermal paste.") 
      (category "Cooling")
      (cf (* ?cf1 0.95)))))

(defrule power-light-no-fan
   ;; IF power light on BUT fans not running
   (symptom (name power-light) (value on) (cf ?cf1))
   (symptom (name fans-running) (value no) (cf ?cf2))
   =>
   (assert (diagnosis 
      (fault "PSU or Fan Connector Fault") 
      (solution "Inspect Power Supply Unit, motherboard, and fan connectors.") 
      (category "Power")
      (cf (* (min ?cf1 ?cf2) 0.85)))))

;; ---------------------------------------------------------
;; Category: Monitor and Display Damage
;; Specificity Note: This rule has 4 conditions, making it 
;; more specific than general display rules.
;; ---------------------------------------------------------

(defrule monitor-physical-damage
   (declare (salience 10)) ;; High Salience to ensure specificity fires first
   (symptom (name power-button) (value on))
   (symptom (name image-displayed) (value no))
   (symptom (name artifacts) (value lines-or-blocks)) ;; combined for brevity
   (symptom (name image-symmetry) (value asymmetric-random))
   (symptom (name cf) (value ?cf1)) ;; Accessing CF of the set
   =>
   (assert (diagnosis 
      (fault "Monitor/LCD Physical Damage (Hypothesis H01)") 
      (solution "The Monitor is damaged; replace LCD.") 
      (category "Display")
      (cf (* ?cf1 0.95)))))

;; ---------------------------------------------------------
;; Category: Motherboard, CPU, and Power Supply Logic
;; ---------------------------------------------------------

(defrule psu-connection-fault
   ;; IF Shutdown AND Power Cable Improper AND Mains Stable
   (symptom (name system-state) (value shutdown))
   (symptom (name psu-cable) (value improper))
   (symptom (name mains-voltage) (value stable))
   =>
   (assert (diagnosis 
      (fault "Power Supply Connection Issue (D03)") 
      (solution "Secure the power cable connection to the PSU.") 
      (category "Motherboard/Power")
      (cf 0.9))))

(defrule disk-boot-failure
   ;; IF On-No-Boot AND Message "DISK BOOT FAILURE"
   (symptom (name system-state) (value on-no-boot))
   (symptom (name error-message) (value disk-boot-failure))
   =>
   (assert (diagnosis 
      (fault "Hard Disk Problem (D05)") 
      (solution "Check boot order and HDD connections.") 
      (category "Motherboard/HDD")
      (cf 0.95))))

(defrule ram-problem-beeps
   ;; IF On-No-Boot AND Repeated Long Beeps
   (symptom (name system-state) (value on-no-boot))
   (symptom (name beep-pattern) (value repeated-long))
   =>
   (assert (diagnosis 
      (fault "RAM Problem (D06)") 
      (solution "Reseat RAM or replace sticks.") 
      (category "Motherboard/RAM")
      (cf 0.9))))

(defrule processor-overheat-logic
   ;; IF On-No-Boot AND Processor Overheating
   (symptom (name system-state) (value on-no-boot))
   (symptom (name component-status) (value cpu-hot))
   =>
   (assert (diagnosis 
      (fault "Processor Problem (D08)") 
      (solution "Check CPU cooling system.") 
      (category "Motherboard/CPU")
      (cf 0.9))))

;; ---------------------------------------------------------
;; Category: BIOS and POST Beep Errors (Fuzzy Logic)
;; ---------------------------------------------------------

(defrule beep-short-post-ok
   (symptom (name beep-duration) (value very-short))
   =>
   (assert (diagnosis (fault "System OK") (solution "Normal POST.") (category "BIOS") (cf 1.0))))

(defrule beep-short-error
   (symptom (name beep-duration) (value short))
   =>
   (assert (diagnosis (fault "POST Error") (solution "Check screen for error code.") (category "BIOS") (cf 0.8))))

(defrule beep-long-mobo
   (symptom (name beep-duration) (value long))
   =>
   (assert (diagnosis (fault "System Board Problem") (solution "Check Motherboard.") (category "BIOS") (cf 0.8))))

(defrule beep-continuous
   (symptom (name beep-duration) (value continuous))
   =>
   (assert (diagnosis (fault "Critical Power/Board/Keyboard Fault") (solution "Check PSU, Mobo, and Keyboard.") (category "BIOS") (cf 0.8))))

;; ---------------------------------------------------------
;; Category: Component-Level Power Circuitry
;; ---------------------------------------------------------

(defrule scr-damage
   (symptom (name dc-output) (value none))
   (symptom (name primary-circuit) (value good))
   (symptom (name oscillation) (value none))
   =>
   (assert (diagnosis 
      (fault "SCR (Silicon Controlled Rectifier) Damaged") 
      (solution "Replace the SCR in the power protection circuit.") 
      (category "Circuitry")
      (cf 0.95))))

;; ---------------------------------------------------------
;; Category: General Troubleshooting (Low Specificity)
;; ---------------------------------------------------------

(defrule ram-screen-distortion
   ;; General rule (Low Salience to fire last)
   (declare (salience -10))
   (symptom (name screen-image) (value distorted))
   =>
   (assert (diagnosis 
      (fault "RAM Fault") 
      (solution "Reseat or replace RAM.") 
      (category "General")
      (cf 0.6)))) ;; Lower certainty for general rules

;; =========================================================
;; 3. REPORTING (Output)
;; =========================================================

(defrule print-diagnosis
   (declare (salience -100)) ;; Force this to run last
   ?d <- (diagnosis (fault ?f) (solution ?s) (cf ?c))
   =>
   (printout t "--------------------------------------------------" crlf)
   (printout t "DIAGNOSIS FOUND:" crlf)
   (printout t "Fault: " ?f crlf)
   (printout t "Solution: " ?s crlf)
   (printout t "Certainty Factor: " ?c crlf)
   (printout t "--------------------------------------------------" crlf))
