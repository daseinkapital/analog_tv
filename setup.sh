SYSTEM = 'pi'

if [[ SYSTEM == 'pi' ]]; then
    echo "Intalling MPV"
    sudo apt-get install mpv
    echo "Installing python3"
    sudo apt-get install python3
    echo "Installing python3-pip"
    sudo apt-get install python3-pip
    echo "Installing python3-venv"
    sudo apt-get install python3-venv
elif [[ SYSTEM == 'mac' ]]; then
    brew install mpv python3 python3-pip python-venv

if [ ! -d "./FieldStation42" ]; then
    echo "Cloning FieldStation42"
    git clone https://github.com/shane-mason/FieldStation42.git
    cd FieldStation42
else
    echo "FieldStation42 exists. Skipping clone."
fi

if [ ! -d "./FieldStation42/catalog" ]; then
    echo "Initiating FieldStation42 setup script."
    chmod +x ./FieldStation42/install.sh
    ./FieldStation42/install.sh
    echo "Starting virtual environment"
    source ./FieldStation42/env/bin/activate
    echo "Moving channel configurations into confs"
    cp -a ./confs/. ./confs/
else
    echo "Install has already been run."