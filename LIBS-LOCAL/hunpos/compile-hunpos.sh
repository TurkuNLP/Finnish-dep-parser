svn checkout http://hunpos.googlecode.com/svn/trunk/ hunpos-read-only
cd hunpos-read-only
./build.sh release linux

#...and if successful
cp _build/hunpos-1.0-linux/hunpos-tag _build/hunpos-1.0-linux/hunpos-tag ..
