# -*- mode: ruby -*-
# vi: set ft=ruby :

$machine_addr = "192.168.80.33"

$machine_cap  = "90"
$machine_cpus = "2"
$machine_name = "ubuntu-musketeer-client"
$machine_ram  = "4096"


$provision_root = <<'SCRIPT_ROOT'

apt-get update
apt-get upgrade

apt-get install -y ca-certificates curl coreutils jq zip python3 python3-pip

SCRIPT_ROOT


$provision_user = <<'SCRIPT_USER'

echo "Upgrading pip"
python3 -m pip install --upgrade pip

echo "Adding local pip to the path"
export PATH=${HOME}/.local/bin/:${PATH}

echo "pip, installing dependencies"
pip3 install --user certifi urllib3[secure] six==1.12
pip3 install --user virtualenv virtualenvwrapper
pip3 install --user pytest pylint
pip3 install --user --upgrade six
pip3 install --user --upgrade matplotlib
pip3 install --user --upgrade jupyter
pip3 install --user --upgrade pandas
pip3 install --user --upgrade pygam
pip3 install --user -r /vagrant/requirements.txt

jupyter notebook --generate-config

#Set up some niceities in the shell
cat <<'EOF_BASHRC' > $HOME/.bashrc

# http://stackoverflow.com/questions/9457233/unlimited-bash-history
export HISTFILESIZE=
export HISTSIZE=
export HISTTIMEFORMAT="[%F %T] "
export HISTFILE=/vagrant/bash_history
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

alias ls='ls --color=auto'
export PS1='\n\@ \w \e[0;32m $(__git_ps1 "(%s)") \e[m \n: \u@\h \j %; '
export PS1='\[\e]0;\u@\h: \w\a\]\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\n$ '

cd /vagrant

EOF_BASHRC

cat <<'EOF_VIM' > $HOME/.vimrc
set hlsearch
set showmode
set showmatch
set noautoindent
set esckeys

set scrolloff=3

" configure expanding of tabs for various file types
au BufRead,BufNewFile *.py set autoindent
au BufRead,BufNewFile *.py set expandtab
au BufRead,BufNewFile *.py set tabstop=4
au BufRead,BufNewFile *.py set softtabstop=4
au BufRead,BufNewFile *.py set shiftwidth=4

" configure expanding of tabs for various file types
au BufRead,BufNewFile *.yaml set autoindent
au BufRead,BufNewFile *.yaml set expandtab
au BufRead,BufNewFile *.yaml set shiftwidth=2
au BufRead,BufNewFile *.yaml set softtabstop=2
au BufRead,BufNewFile *.yaml set tabstop=2

EOF_VIM

SCRIPT_USER


Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"

  config.vm.provision :shell, inline: $provision_root
  config.vm.provision :shell, privileged: false, inline: $provision_user
  config.vm.network "forwarded_port", host_ip: "127.0.0.1", guest: 8888, host: 8881, auto_correct: true
  config.vm.network "forwarded_port", host_ip: "127.0.0.1", guest: 8001, host: 8001, auto_correct: true

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--name", $machine_name]
    vb.customize ["modifyvm", :id, "--cpus", $machine_cpus]
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", $machine_cap]
    vb.customize ["modifyvm", :id, "--memory", $machine_ram]
  end

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  config.vm.hostname = $machine_name
  config.vm.network :private_network, ip: $machine_addr
end
