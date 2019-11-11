#!/bin/bash

for i in `seq 17 32`;
do
#	echo $i
	rosrun ar_track_alvar createMarker $i
done
