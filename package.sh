package_dir="./PicoSync"

# create necessary direcotries
mkdir -p $package_dir
mkdir -p $package_dir/.sources

# copy files
cp monitor.py $package_dir/.sources
cp main.py $package_dir/.sources
cp set_queue.py $package_dir/.sources
cp install.sh $package_dir/