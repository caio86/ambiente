saida() {
	echo "Usage: ./run-scenario.sh [ scenario ]"
	echo "Available scenarios:"
	ls scenarios
	exit 1	
}

if [ -z $1 ] || [ ! -d scenarios/$1 ]; then
	saida	
fi

vagrant up --provision
vagrant ssh-config > ssh_config

ansible-playbook scenarios/$1/server.yml
ansible-playbook scenarios/$1/client.yml
