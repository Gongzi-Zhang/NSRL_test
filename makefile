SHELL       := /bin/bash
CXXFLAGS    := -std=c++2a
VPATH	    := include

root_libs    = `root-config --libs --cflags`

# include file
calo	    := calo.h
utilities   := utilities.h
convert	    := convert.h

cali_include = calo.h utilities.h convert.h 

convert: convert.C $(cali_include)
	g++ $(CXXFLAGS) -o $@ $^ $(root_libs)
	mv convert bin/

all: convert
# vim: set shiftwidth=4 softtabstop=4 tabstop=8: #
