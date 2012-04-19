rem this batch file is used to CLEAN/REMOVE the RabbitMQ
rem VHost, Users and permissions used by the MACTS project

@pause

rem change to the RabbitMQ directory
cd "C:\Program Files (x86)\RabbitMQ Server\rabbitmq_server-2.8.1\sbin"

rem create the VHOST
call rabbitmqctl.bat delete_vhost macts

rem delete the USERS
call rabbitmqctl delete_user liaison
call rabbitmqctl delete_user metrics
call rabbitmqctl delete_user agent

rem call rabbitmqctl delete_user collab
rem call rabbitmqctl delete_user command
rem call rabbitmqctl delete_user sense
rem call rabbitmqctl delete_user safety

call rabbitmqctl list_users

cd \macts\source\macts\
@pause