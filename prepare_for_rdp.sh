
set -eu

sudo apt update && sudo apt upgrade -y

# sudo passwd ubuntu


sudo apt install xrdp xfce4 xfce4-goodies tightvncserver -y


echo xfce4-session> /home/ubuntu/.xsession

sudo cp /home/ubuntu/.xsession /etc/skel

sudo sed -i '0,/-1/s//ask-1/' /etc/xrdp/xrdp.ini


sudo service xrdp restart

sudo apt install obs-studio ffmpeg -y


sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly


sudo apt-get install pulseaudio pulseaudio-utils pavucontrol

pulseaudio --start