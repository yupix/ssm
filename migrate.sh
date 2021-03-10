#!/usr/bin/env bash

input_comment() {
	echo "please input comment"
	read -r -p ">" comment
}

upgrade() {
	alembic upgrade +1
}

downgrade() {
	alembic downgrade -1
}

echo "please input your use action type"
cat <<EOF
1.generate
2.upgrade
3.downgrade
4.clean
EOF
read -r -p '>' action_type

case ${action_type} in
'1')
	input_comment
	alembic revision --autogenerate -m "${action_type} ${comment}"
	cat <<EOF
1.upgrade
2.downgrade
EOF
	read -r -p '>' action_type
	case ${action_type} in
	'1')
		upgrade
		;;
	'2')
		downgrade
		;;
	esac
	;;

'2')
	upgrade
	;;
'3')
	downgrade
	;;
'4')
	rm -rf ./alembic/versions/*
;;

esac
