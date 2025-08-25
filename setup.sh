SYSTEM = 'pi'

if [[ SYSTEM == 'pi' ]]; then
    echo "Intalling MPV"
    sudo apt-get install mpv
    if type "python3" > /dev/null; then
        echo "Found python3 - using that"
    else
        echo "Installing python3"
        sudo apt-get install python3
    fi
elif [[ SYSTEM == 'mac' ]]; then
    brew install mpv python3
fi

if [ ! -d "./FieldStation42/fs42" ]; then
    echo "Cloning FieldStation42"
    git clone https://github.com/shane-mason/FieldStation42.git
    cd FieldStation42
else
    echo "FieldStation42 exists. Skipping clone."
fi

if [ ! -d "./FieldStation42/catalog" ]; then
    cd FieldStation42
    echo "Initiating FieldStation42 setup script."
    chmod +x ./install.sh
    bash ./install.sh
    echo "Moving channel configurations into confs"
    cp -a ./confs/. ./confs/
else
    echo "Install has already been run."
    cd FieldStation42
fi

echo "Starting virtual environment"

source env/Scripts/activate