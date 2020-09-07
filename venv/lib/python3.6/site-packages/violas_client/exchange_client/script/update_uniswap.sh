#########################################################################
# File Name: script.sh
# Author: ma6174
# mail: ma6174@163.com
# Created Time: 2019年12月12日 星期四 13时26分30秒
#########################################################################
#!/bin/bash

for file in $(ls ./move_build_output/modules/*.mv)
do
	echo $file
	python3 ./parse_code.py ./uniswap.data $file
done


for file in $(ls ./move_build_output/scripts/*.mv)
do
	echo $file
	python3 ./parse_code.py ./uniswap.data $file
done
