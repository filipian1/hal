
(cl:in-package :asdf)

(defsystem "hal-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :std_msgs-msg
)
  :components ((:file "_package")
    (:file "Floats" :depends-on ("_package_Floats"))
    (:file "_package_Floats" :depends-on ("_package"))
  ))