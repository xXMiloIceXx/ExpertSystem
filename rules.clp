;;; ============================================
;;; Knowledge Base: Computer Hardware Diagnosis
;;; ============================================

(deftemplate diagnosis
   (slot message))

;;; Rule 1: Power Supply Failure
;;; If the PC does not power on, the PSU is likely faulty
(defrule psu-failure
   (power-on no)
   =>
   (assert (diagnosis
      (message "Check the power supply unit (PSU) and power cables."))))

;;; Rule 2: Motherboard Failure
;;; Power off with beeps indicates motherboard issues
(defrule motherboard-failure
   (power-on no)
   (beeps yes)
   =>
   (assert (diagnosis
      (message "Possible motherboard failure. Inspect motherboard components."))))

;;; Rule 3: RAM Issue
;;; Beeps with no display often indicate RAM problems
(defrule ram-issue
   (power-on yes)
   (beeps yes)
   (screen-black yes)
   =>
   (assert (diagnosis
      (message "Possible RAM issue. Reseat or replace RAM modules."))))

;;; Rule 4: GPU Failure
;;; No beeps and no display suggest GPU or display failure
(defrule gpu-issue
   (power-on yes)
   (beeps no)
   (screen-black yes)
   =>
   (assert (diagnosis
      (message "Check the graphics card and its power connection."))))

;;; Rule 5: Display Cable or Monitor Issue
;;; System runs but no display output
(defrule display-cable-issue
   (power-on yes)
   (screen-black yes)
   =>
   (assert (diagnosis
      (message "Check the display cable or try another monitor."))))

;;; Rule 6: Overheating
;;; Sudden shutdown indicates thermal problems
(defrule overheating
   (power-on yes)
   (sudden-shutdown yes)
   =>
   (assert (diagnosis
      (message "System overheating detected. Check CPU fan and airflow."))))

;;; Rule 7: Boot Device Failure
;;; Power on but no screen suggests boot issues
(defrule boot-device-failure
   (power-on yes)
   (screen-black yes)
   =>
   (assert (diagnosis
      (message "Possible boot device failure. Check storage and BIOS settings."))))

;;; Rule 8: Normal Operation
;;; System functions as expected
(defrule normal-operation
   (power-on yes)
   (screen-black no)
   =>
   (assert (diagnosis
      (message "System appears to be operating normally."))))

;;; Rule 9: CMOS Battery (New)
(defrule cmos-battery-failure
   (power-on yes)
   (time-reset yes)
   =>
   (assert (diagnosis (message "CMOS Battery is likely dead. Replace the CR2032 battery."))))

;;; Rule 10: Storage Failure (New)
(defrule storage-failure
   (power-on yes)
   (error-boot-device yes)
   =>
   (assert (diagnosis (message "Storage failure detected. Check HDD/SSD cables or BIOS settings."))))

;;; Rule 11: Fallback (Ensures something is always found)
(defrule fallback-check
   (power-on yes)
   (screen-black no)
   (sudden-shutdown no)
   (time-reset no)
   (error-boot-device no)
   =>
   (assert (diagnosis (message "This case will be reviewed to improve the knowledge base."))))