cd matrix
echo "Running rgbmatrix installation..."
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
make build-python
sudo make install-python
cd bindings
sudo pip install -e python/
cd ../../
echo "Installing required dependencies. This may take some time (10 minutes-ish)..."
sudo apt-get install libxml2-dev libxslt-dev
sudo pip install mlbgame==2.4.2 pytz tzlocal
make
echo "Installation complete. Play around with the examples in matrix/bindings/python/samples, or make your config file and turn on your scoreboard!"
