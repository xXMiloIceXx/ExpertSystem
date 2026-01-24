;;; Rules for Computer Hardware Fault Diagnosis
(deftemplate diagnosis (slot message))

(defrule power-supply-failure
   (power-on no)
   =>
   (assert (diagnosis (message "Check the PSU and power cables."))))

(defrule ram-issue
   (power-on yes)
   (beeps yes)
   (screen-black yes)
   =>
   (assert (diagnosis (message "Possible RAM failure. Clean the contacts."))))

(defrule gpu-issue
   (power-on yes)
   (beeps no)
   (screen-black yes)
   =>
   (assert (diagnosis (message "Check the GPU or monitor cable."))))