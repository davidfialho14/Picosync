#!/bin/bash

# OUTPUT FILE
output_file=/dev/null

# change to script directory
cd $(dirname "$0")

echo "installing..."

# mark the time and date that the script was executed
# and create new log file
date > $output_file

if ! which python >> /dev/null ; then
	# install python
	echo "installing python..."
	sudo apt-get install -y python >> $output_file 2>&1 || echo "python installation failed" && exit
	echo "python installed"
fi

echo "installing necessary modules..."

# check if pip is installed
if ! which pip >> /dev/null ; then
	# install pip
	sudo apt-get install -y python-pip >> $output_file 2>&1 || echo "pip installation failed" && exit
fi

# install dropbox module
sudo pip install dropbox >> $output_file 2>&1 || echo "dropbox module installation failed"

# install watchdog
sudo pip install watchdog >> $output_file 2>&1 || echo "watchdog module installation failed"

echo "modules installed"

# installation directory
install_dir="/opt/picosync"

# create installation directory
sudo mkdir -p $install_dir
# copy needed sources to the installation directory
sudo rm -rf	$install_dir/sources
sudo cp -fR .sources/ $install_dir/sources

# create execution script
sudo sh -c "echo '#!/bin/bash \npython /opt/picosync/sources/main.py \$@' > $install_dir/picosync"
# give execution permissions for the execution script
sudo chmod +x $install_dir/picosync
# create link to installation script in the bin directory
sudo ln -sf $install_dir/picosync /usr/bin/picosync

echo "installed successfully"
echo "\nto execute run: picosync"