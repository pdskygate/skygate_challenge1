#!/bin/sh

declare -a arr=("manage.py migrate"
                "manage.py loaddata answer_possibility"
                "manage.py loaddata question_type"
                "manage.py loaddata question"
				"manage.py create_data")

for command in "${arr[@]}"
do
{
	python $command
} || {
	echo "Error during executing command:"
	echo $command
	echo "Contant with technical support sending above log"
	exit 1
}
done
echo "DEPLOYMENT DONE"