rem this batch file is used to create the RabbitMQ
rem VHost, Exchanges and Users needed by the MACTS project

@pause

rem change to the RabbitMQ directory
cd "C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-2.6.0\sbin"

rem create the VHOST
call rabbitmqctl add_vhost macts
rem call rabbitmqctl list_exchanges -p macts

rem create the USERS
call rabbitmqctl add_user liaison talker
call rabbitmqctl add_user collab fab
call rabbitmqctl add_user metrics countem
call rabbitmqctl add_user command nasa
call rabbitmqctl add_user sense isee
call rabbitmqctl add_user safety cone
call rabbitmqctl list_users

rem PERMISSIONS
rem the liaison account has full permissions
rem it can configure, write and read any resource
call rabbitmqctl set_permissions -p macts liaison ".*" ".*" ".*"
call rabbitmqctl set_permissions -p macts collab "^shared-.*" "^shared-.*" "^shared-.*"
call rabbitmqctl set_permissions -p macts metrics "^metrics.*" "^metrics.*" "^metrics.*"
call rabbitmqctl set_permissions -p macts command "command|response" "command|response" "command|response"
call rabbitmqctl set_permissions -p macts sense "^sensor-.*" "^sensor-.*" "^sensor-.*"
call rabbitmqctl set_permissions -p macts safety "" "sumo-control" ""

call rabbitmqctl list_permissions -p macts

@pause