import os, sys, subprocess
import glob, shutil
import time

# Environment Variables
rabbitmq_name = "rabbitmq"
rabbitmq_namespace = "rabbitmq"
replica_count = "3"
requests_cpu = "1"
limits_cpu = "2"
requests_memory = "2Gi"
limits_memory = "4Gi"
channel_max = "2000"
ingress_class = "nginx"
ingress_namespace = "nginx"
ingress_host = "rabbitmq.example.com"

admin = {"username": "admin",
         "password": "admin12345"}

users = {"vhost01": ["user01","password01"],
         "vhost02": ["user02","password02"],
         "vhost03": ["user03","password03"]}

tags = "monitoring management"

def replace_word(infile,old_word,new_word):
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: " + infile)
        sys.exit(1)

    f1=open(infile,'r').read()
    f2=open(infile,'w')
    m=f1.replace(old_word,new_word)
    f2.write(m)

def deploy():
    print("Deploying RabbitMQ!")
    print("-------------------------------")
         
    current_dir = os.getcwd()
    manifest_files = glob.glob(f"{current_dir}/*.yaml")
    replaced_folder = f"{current_dir}/manifest_files"

    if not os.path.exists(replaced_folder):
        os.makedirs(replaced_folder)
    else:
        shutil.rmtree(replaced_folder)
        os.makedirs(replaced_folder)

    for files in manifest_files:
        shutil.copy2(files, replaced_folder)

    list_files = []
    if os.path.exists(replaced_folder):
        for dirpath, dirnames, filenames in os.walk(replaced_folder):
            for file in filenames:
                manifest_file = f"{dirpath}/{file}"
                replace_word(manifest_file, '__rabbitmq_name__', rabbitmq_name)
                replace_word(manifest_file, '__rabbitmq_namespace__', rabbitmq_namespace)
                replace_word(manifest_file, '__replica_count__', replica_count)
                replace_word(manifest_file, '__requests_cpu__', requests_cpu)
                replace_word(manifest_file, '__limits_cpu__', limits_cpu)
                replace_word(manifest_file, '__requests_memory__', requests_memory)
                replace_word(manifest_file, '__limits_memory__', limits_memory)
                replace_word(manifest_file, '__channel_max__', channel_max)
                replace_word(manifest_file, '__ingress_class__', ingress_class)
                replace_word(manifest_file, '__ingress_host__', ingress_host)
                replace_word(manifest_file, '__ingress_namespace__', ingress_namespace)
                replace_word(manifest_file, '__admin_user__', admin["username"])
                replace_word(manifest_file, '__admin_pass__', admin["password"])
                list_files.append(f"{replaced_folder}/{file}")

    for file in list_files:
        cmd = f"kubectl apply -f {file}"
        subprocess.call(cmd, shell=True, universal_newlines=True)
    print("-------------------------------")

def status():
    cmd = f"kubectl exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl status"
    stdout = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if stdout == 0:
        print("StatefulSet completed successfully!")
    else:
        print("Waiting 180 seconds for StatefulSet to complete rolled out...")
        time.sleep(180)
        stdout = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if stdout == 0:
            print("StatefulSet completed successfully!")
        else:
            print("StatefulSet taking too long to complete, you need to manual install...")
            exit(1)
    print("-------------------------------")

def vhost():
    print("Creating Virtual Hosts and Application Users")
    print("-------------------------------")
    for vhost, credentials in users.items():
        create_vhost = f'kubectl exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl add_vhost {vhost}'
        create_credentianls = f'kubectl exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl add_user {credentials[0]} {credentials[1]}'
        set_tags = f"kubectl exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl set_user_tags {credentials[0]} {tags}"
        set_permissions = f'kubectl exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl set_permissions -p {vhost} {credentials[0]}  ".*" ".*" ".*"'

        subprocess.call(create_vhost, shell=True, universal_newlines=True)
        subprocess.call(create_credentianls, shell=True, universal_newlines=True)
        subprocess.call(set_tags, shell=True, universal_newlines=True)
        subprocess.call(set_permissions, shell=True, universal_newlines=True)
    print("-------------------------------")

def policy():
    print("Configuring HA policy!")
    print("-------------------------------")
    list_vhosts = f"kubectl -it exec rabbitmq-server-{int(replica_count)-1} -n {rabbitmq_namespace} -- rabbitmqctl list_vhosts | grep -v -e 'name' -e 'Listing vhosts' | sort -r"
    stdout = subprocess.Popen(list_vhosts, shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
    for vhost in stdout.split('\n'):
        if vhost != "":
            set_policy = "kubectl exec rabbitmq-server-%s -n %s -- rabbitmqctl set_policy -p \"%s\" ha-all-%s \"\" '{\"ha-mode\":\"all\",\"ha-sync-mode\":\"automatic\"}';" % (int(replica_count)-1, rabbitmq_namespace, vhost, vhost)
            subprocess.call(set_policy, shell=True, universal_newlines=True)
    print("-------------------------------")

def main():
    deploy()
    status()
    vhost()
    policy()

if __name__== "__main__":
    main()
