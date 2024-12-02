
1 Compile on Linux

2 Use a tool named buildozer

3 Commands(from readthedocs):
pip3 install --user --upgrade buildozer
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.33 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/

# run buildoze init to get the buildozer.spec file
buildozer init
# this will build a buildozer.spec template for the android app to modify
nano buildozer.spec

# environment activation
source /mnt/storage/android_app/examples/buildozer-env/bin/activate

#verify environment
which python
echo $VIRTUAL_ENV

# compile the buildozer.spec file
buildozer -v android debug

# use the copy script on windows to copy the .apk file into the release dir 


