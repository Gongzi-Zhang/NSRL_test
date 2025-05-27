# Janus_5202_3.6.0_20240514
* Installation
    * OS: Ubuntu 22.04
	* dependency:
	    * libusb-1.0-0-dev
	    * python3-tk
	    * python3-pip
	    * python3-pil.imagetk
    * cd Janus_5202_3.6.0_20240514_linux
    * sudo bash installer_debian.bash 
    * sudo vim /etc/udev/rules.d/50-myusb.rules
    * sudo udevadm control --reload
* Running:
    * cd bin
    * python3 JanusPy.pyw

* Issues
    * Somehow, Janus can only work with 5 CAEN units. No matter it is paralle connection
      or chaining: any 5 of them work fine, with 6 units, janus just freezes
      after starting a new run, and only the first statistics row is enabled, though 
      no update there either.

# DRP
    > sudo nmcli con mod "Wired connection 1" ipv4.addresses "192.168.1.10/24"
    > sudo nmcli con mod "Wired connection 1" ipv4.method manual
    >  sudo nmcli con up "Wired connection 1"
    > Connections


# realVNC
    > realVNC doesn't support wayland: 
    uncomment the following statement in /etc/gdm3/custom.conf
    WaylandEnable=false
    Then reboot the laptop

    > Unsupported authentication scheme:
    In realVNC server:
    option -> security -> VNC password
