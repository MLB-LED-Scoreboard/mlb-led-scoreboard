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
sudo pip install pytz tzlocal feedparser pyowm
sudo pip install git+git://github.com/panzarino/mlbgame.git@365532125b0fe1286c32fa2471c2623e2437ab80#egg=mlbgame
make
echo "Installation complete. Play around with the examples in matrix/bindings/python/samples, or make your config file and turn on your scoreboard!"
