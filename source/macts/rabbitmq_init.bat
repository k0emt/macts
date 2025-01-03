rem this batch file is used to create the RabbitMQ
rem VHost, Exchanges and Users needed by the MACTS project

@pause

rem change to the RabbitMQ directory
cd "C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-2.8.1\sbin"

rem create the VHOST
call rabbitmqctl add_vhost macts
rem call rabbitmqctl list_exchanges -p macts

rem create the USERS
call rabbitmqctl add_user liaison talker
call rabbitmqctl set_user_tags liaison administrator

call rabbitmqctl add_user metrics countem
call rabbitmqctl add_user agent xrosslite

rem call rabbitmqctl add_user collab fab
rem call rabbitmqctl add_user command nasa
rem call rabbitmqctl add_user sense isee
rem call rabbitmqctl add_user safety cone
call rabbitmqctl list_users

rem PERMISSIONS
rem the liaison account has full permissions
rem it can configure, write and read any resource
call rabbitmqctl set_permissions -p macts liaison ".*" ".*" ".*"
call rabbitmqctl set_permissions -p macts metrics ".*" ".*" ".*"
call rabbitmqctl set_permissions -p macts agent ".*" ".*" ".*"

rem call rabbitmqctl set_permissions -p macts collab ".*" ".*" ".*"
rem call rabbitmqctl set_permissions -p macts command ".*" ".*" ".*"
rem call rabbitmqctl set_permissions -p macts sense ".*" ".*" ".*"
rem call rabbitmqctl set_permissions -p macts safety ".*" ".*" ".*"

call rabbitmqctl list_permissions -p macts

cd \macts\source\macts\
@pause