cd /home/pi/brew/


FILE=update/update.tar.gz
if test -f "$FILE"; then
	tar -xzvf update/update.tar.gz --overwrite
	rm update/update.tar.gz
    echo "$FILE exist."
else 
    echo "$FILE does not exist."
fi

lxterminal -e "python3 /home/pi/brew/main.py"

cd /