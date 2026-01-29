;; =========================================================
;; 1. TEMPLATES
;; =========================================================

(deftemplate symptom
   (slot name) (slot value) (slot cf (type FLOAT) (default 1.0)))

(deftemplate diagnosis
   (slot fault) (slot solution) (slot category) (slot citation) (slot cf (type FLOAT) (default 0.0)))

;; =========================================================
;; 2. AUDIO & SOUND RULES (整合 Source A & B)
;; =========================================================

;; [Source A] Driver Issue
;; Rule: IF audio bar moving BUT no sound -> Missing Driver
(defrule audio-driver-software
   (symptom (name volume-bar) (value bar-moving) (cf ?c1))
   (symptom (name sound-output) (value sound-none) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.95))
   (assert (diagnosis 
      (fault "Missing or Corrupt Audio Driver") 
      (solution "Update Audio Drivers via Device Manager.") 
      (category "Audio/Software") 
      (citation "Jern et al. (2021)")
      (cf ?final_cf))))

;; [Source A] Speaker Hardware
;; Rule: IF sound is scratchy/distorted -> Faulty Speaker
(defrule audio-hardware-speaker
   (symptom (name sound-quality) (value sound-distorted) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 0.9))
   (assert (diagnosis 
      (fault "Faulty Speaker (Hardware)") 
      (solution "Replace the laptop speaker unit.") 
      (category "Audio/Hardware") 
      (citation "Jern et al. (2021)")
      (cf ?final_cf))))

;; [Source A] Interference
;; Rule: IF volume fluctuates irregularly -> External Interference
(defrule audio-interference
   (symptom (name volume-behavior) (value bar-irregular) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 0.7))
   (assert (diagnosis 
      (fault "External Audio Interference") 
      (solution "Check for electromagnetic interference or loose cables.") 
      (category "Audio") 
      (citation "Jern et al. (2021)")
      (cf ?final_cf))))

;; [Source B] Sound Card Detection
;; Rule: IF sound card not detected -> Damaged/Not Installed
(defrule audio-card-failure
   (symptom (name sound-card-status) (value card-not-detected) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 1.0))
   (assert (diagnosis 
      (fault "Sound Card Failure / Not Detected") 
      (solution "Replace the Sound Card.") 
      (category "Audio/Hardware") 
      (citation "Bassil (2012)")
      (cf ?final_cf))))

;; =========================================================
;; 3. THERMAL & CPU RULES (整合 Source A & B)
;; =========================================================

;; [Source A] Overheating Threshold
;; Rule: IF CPU > 85°C -> Overheating
(defrule cpu-overheat-threshold
   (symptom (name cpu-temp) (value temp-above-85) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 1.0))
   (assert (diagnosis 
      (fault "CPU Overheating (>85°C)") 
      (solution "Clean cooling fans, apply new thermal paste, use cooling pad.") 
      (category "Thermal") 
      (citation "Chinnathampy et al. (2025)")
      (cf ?final_cf))))

;; [Source A] Predictive Overheating
;; Rule: IF unusual rising temp pattern -> Imminent Overheating
(defrule cpu-predictive-overheat
   (symptom (name temp-pattern) (value temp-rising-rapidly) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 0.8))
   (assert (diagnosis 
      (fault "Imminent Overheating Predicted") 
      (solution "Reduce workload or clean the system vents.") 
      (category "Thermal") 
      (citation "Chinnathampy et al. (2025)")
      (cf ?final_cf))))

;; [Source B & Miracle] Boot Warning
;; Rule: IF CPU overheat warning at boot -> Fan/Heatsink
(defrule cpu-boot-warning
   (symptom (name boot-warning) (value warn-cpu-overheat) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 1.0))
   (assert (diagnosis 
      (fault "CPU Fan/Heatsink Failure") 
      (solution "Check CPU fan connection and heatsink contact.") 
      (category "Thermal") 
      (citation "Miracle & Olayemi (2024)")
      (cf ?final_cf))))

;; [Source B] Processor Fault
;; Rule: IF on but not booting AND overheating -> Processor Problem
(defrule processor-hardware-fault
   (symptom (name system-state) (value on-no-boot) (cf ?c1))
   (symptom (name component-status) (value cpu-hot) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.9))
   (assert (diagnosis 
      (fault "Processor (CPU) Hardware Problem (D08)") 
      (solution "Check CPU seating or replace processor.") 
      (category "Motherboard/CPU") 
      (citation "Laksana et al. (2024)")
      (cf ?final_cf))))

;; =========================================================
;; 4. STORAGE RULES (整合 Source A & B)
;; =========================================================

;; [Source A] Wear & Tear
;; Rule: IF random reboots + old device -> Faulty Storage
(defrule storage-wear
   (symptom (name boot-behavior) (value random-reboots) (cf ?c1))
   (symptom (name device-age) (value age-old) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.6))
   (assert (diagnosis 
      (fault "Storage Device Wear & Tear") 
      (solution "Replace the storage device.") 
      (category "Storage") 
      (citation "Jern et al. (2021)")
      (cf ?final_cf))))

;; [Source A & B] SMART Warning
;; Rule: IF SMART warning -> Serious mechanical problems
(defrule hdd-smart-fail
   (symptom (name error-message) (value err-smart-warning) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 1.0))
   (assert (diagnosis 
      (fault "Critical Hard Disk Failure (SMART)") 
      (solution "Backup data immediately and replace drive.") 
      (category "Storage") 
      (citation "Bassil (2012)")
      (cf ?final_cf))))

;; [Source B] Boot Failure Message
;; Rule: IF "DISK BOOT FAILURE" -> HDD Problem
(defrule hdd-boot-failure
   (symptom (name system-state) (value on-no-boot) (cf ?c1))
   (symptom (name error-message) (value err-disk-boot-failure) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 1.0))
   (assert (diagnosis 
      (fault "Hard Disk Boot Sector/Connection Problem (D05)") 
      (solution "Check boot order and HDD connections.") 
      (category "Storage") 
      (citation "Laksana et al. (2024)")
      (cf ?final_cf))))

;; [Source B] IDE Delay
;; Rule: IF IDE not ready -> Drive not spinning fast enough
(defrule hdd-ide-delay
   (symptom (name hdd-status) (value err-ide-not-ready) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 0.85))
   (assert (diagnosis 
      (fault "Hard Disk Spin-up Latency") 
      (solution "Increase Hard Disk pre-delay time in BIOS.") 
      (category "Storage") 
      (citation "Bassil (2012)")
      (cf ?final_cf))))

;; =========================================================
;; 5. DISPLAY RULES (整合 Source A & B)
;; =========================================================

;; [Source A & B] Physical Damage Consensus
;; Rule: IF Power On + No Image + Artifacts -> Monitor Damaged
(defrule monitor-physical-damage
   (symptom (name power-status) (value on) (cf ?c1))
   (symptom (name screen-visuals) (value artifacts) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.95))
   (assert (diagnosis 
      (fault "Monitor/LCD Physical Damage (Hypothesis H01)") 
      (solution "The LCD panel is damaged; replace monitor.") 
      (category "Display") 
      (citation "Kiray & Sianturi (2020)")
      (cf ?final_cf))))

;; [Source B] RAM Caused Distortion
;; Rule: IF screen distorted -> RAM cause
(defrule display-ram-distortion
   (symptom (name screen-visuals) (value distorted-image) (cf ?c1))
   =>
   (bind ?final_cf (* ?c1 0.6)) ;; Lower confidence as it's general
   (assert (diagnosis 
      (fault "RAM Fault Causing Video Distortion") 
      (solution "Reseat or replace RAM.") 
      (category "Memory/Display") 
      (citation "Qurashi et al. (2017)")
      (cf ?final_cf))))

;; =========================================================
;; 6. POWER & STARTUP (整合 Source A & B)
;; =========================================================

;; [Source A & B] Total Power Fail
;; Rule: IF No lights + No fan -> Check Cables/PSU
(defrule power-dead-system
   (symptom (name power-lights) (value light-off) (cf ?c1))
   (symptom (name fan-status) (value fan-silent) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.9))
   (assert (diagnosis 
      (fault "Total Power Failure") 
      (solution "Check power cables, PSU, and electrical outlet.") 
      (category "Power") 
      (citation "Miracle & Olayemi (2024)")
      (cf ?final_cf))))

;; [Source A & B] Partial Power
;; Rule: IF Power Light ON + No Fan -> PSU/Mobo
(defrule power-partial-failure
   (symptom (name power-lights) (value light-on) (cf ?c1))
   (symptom (name fan-status) (value fan-silent) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.85))
   (assert (diagnosis 
      (fault "Power Supply Unit or Motherboard Fault") 
      (solution "Inspect PSU and Motherboard for faults.") 
      (category "Power") 
      (citation "Miracle & Olayemi (2024)")
      (cf ?final_cf))))

;; [Source B] PSU Connection Logic
;; Rule: IF Shutdown + Bad Cable + Stable Mains -> PSU Problem
(defrule psu-connection-logic
   (symptom (name system-state) (value shutdown) (cf ?c1))
   (symptom (name psu-cable) (value loose) (cf ?c2))
   (symptom (name mains-voltage) (value stable) (cf ?c3))
   =>
   (bind ?final_cf (* (min ?c1 ?c2 ?c3) 0.9))
   (assert (diagnosis 
      (fault "Power Supply Connection Issue (D03)") 
      (solution "Secure the power cable connection to the PSU.") 
      (category "Power") 
      (citation "Laksana et al. (2024)")
      (cf ?final_cf))))

;; [Source B] SCR Circuit Damage (Deep Hardware)
;; Rule: No DC + No Oscillation -> SCR Damaged
(defrule circuit-scr-damage
   (symptom (name dc-output) (value none) (cf ?c1))
   (symptom (name oscillation) (value none) (cf ?c2))
   =>
   (bind ?final_cf (* (min ?c1 ?c2) 0.95))
   (assert (diagnosis 
      (fault "SCR (Silicon Controlled Rectifier) Damaged") 
      (solution "Replace SCR in power protection circuit.") 
      (category "Circuitry") 
      (citation "Jing & Julan (1997)")
      (cf ?final_cf))))

;; =========================================================
;; 7. BEEP CODES (Source B - Fuzzy Logic)
;; =========================================================

(defrule beep-post-normal
   (symptom (name beep-duration) (value beep-very-short) (cf ?c1))
   =>
   (assert (diagnosis (fault "System OK (Normal POST)") (solution "Hardware is functioning.") (category "Info") (citation "Bassil (2012)") (cf ?c1))))

(defrule beep-post-error
   (symptom (name beep-duration) (value beep-short) (cf ?c1))
   =>
   (assert (diagnosis (fault "General POST Error") (solution "Check screen for error code.") (category "BIOS") (citation "Bassil (2012)") (cf (* ?c1 0.8)))))

(defrule beep-system-board
   (symptom (name beep-duration) (value beep-long) (cf ?c1))
   =>
   (assert (diagnosis (fault "System Board Problem") (solution "Check Motherboard.") (category "BIOS") (citation "Bassil (2012)") (cf (* ?c1 0.8)))))

(defrule beep-ram-failure
   (symptom (name beep-code) (value beep-repeated-long) (cf ?c1))
   =>
   (assert (diagnosis (fault "RAM Problem (G10->D06)") (solution "Reseat RAM sticks.") (category "Memory") (citation "Laksana et al. (2024)") (cf (* ?c1 0.9)))))

(defrule beep-continuous-failure
   (symptom (name beep-duration) (value beep-continuous) (cf ?c1))
   =>
   (assert (diagnosis (fault "Critical Power/Board/Keyboard Fault") (solution "Check PSU, Mobo, and Keyboard.") (category "BIOS") (citation "Bassil (2012)") (cf (* ?c1 0.8)))))

;; =========================================================
;; 8. META-RULES: CONFLICT RESOLUTION (Higher Order Logic)
;; =========================================================

(defrule resolve-conflict-system-ok
   (declare (salience -10))

   ?ok_fact <- (diagnosis (category "Info"))

   (diagnosis (category ~"Info"))

   =>

   (retract ?ok_fact)
   
   (printout t ">>> [Meta-Rule] Logical Conflict Detected: Faults exist. Retracting 'System OK' status." crlf))