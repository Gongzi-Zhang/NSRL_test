SHELL       := /bin/bash
CXXFLAGS    := -std=c++2a
VPATH	    := include

sqlite3_libs = -l sqlite3
root_libs    = `root-config --libs --cflags`

# include file
calo	    := calo.h
utilities   := utilities.h
convert	    := convert.h

cali_include = calo.h utilities.h convert.h 

convert: convert.C $(cali_include)
	g++ $(CXXFLAGS) -o $@ $^ $(root_libs)
	mv convert bin/

zdc: zdc.C
	g++ $(CXXFLAGS) -o $@ $^ $(sqlite3_libs) $(root_libs)                   
	mv $@ bin/   

all: zdc
# vim: set shiftwidth=4 softtabstop=4 tabstop=8: #
