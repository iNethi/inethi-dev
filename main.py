import sys
import ansible_runner
import pathlib


def my_status_handler(data, runner_config):
    print('Status...')
    print(data['status'])


def my_event_handler(data):
    if data.get('event_data'):
        event_data = data['event_data']
        if event_data.get('name'):
            print(event_data['name'])


def write_to_inventory(ip, user, password, inventory_path):
    with open(inventory_path, 'w') as f:
        f.write(f"[localserver]\n")
        f.write(f"{ip} ansible_user='{user}' ansible_password='{password}' "
                f"ansible_ssh_common_args='-o StrictHostKeyChecking=no' ansible_become_pass='{password}'\n")


def run_playbook(playbook_name, playbook_dir_path, inventory_path):
    playbook_path = f"{playbook_dir_path}/{playbook_name}.yml"
    r = ansible_runner.run(private_data_dir=inventory_path, playbook=playbook_path, inventory=inventory_path,
                           status_handler=my_status_handler, quiet=False, event_handler=my_event_handler)

    # Check if playbook run was successful
    if r.rc != 0:
        print(f"Error running playbook: {playbook_name}")
        sys.exit(1)


def main():
    abs_path = pathlib.Path(__file__).parent.resolve()
    choices = ['jellyfin', 'nextcloud', 'splash-screen', 'radiusdesk', 'wordpress', 'updater', 'keycloak']
    traefik = 'traefik'
    test_server = "test_server_connection"
    system_requirements = "system_requirements"
    playbook_dir_path = f"{abs_path}/playbooks"
    inventory_path = f"{abs_path}/inventory"

    # Prompt user for IP, username, and password
    ip = input("Enter your IP address: ")
    user = input("Enter your username: ")
    password = input("Enter your password: ")

    # Write to inventory file
    write_to_inventory(ip, user, password, inventory_path)

    # Run initial playbooks
    run_playbook(test_server, playbook_dir_path, inventory_path)
    run_playbook(system_requirements, playbook_dir_path, inventory_path)
    run_playbook(traefik, playbook_dir_path, inventory_path)

    # Prompt user to select services to install
    print("Select services to install:")
    for idx, choice in enumerate(choices, 1):
        print(f"{idx}. {choice}")

    selected_indexes = input("Enter the numbers of the services you want to install (comma-separated): ").split(',')
    selected_services = [choices[int(idx) - 1] for idx in selected_indexes]

    # Run playbooks for selected services
    for service in selected_services:
        run_playbook(service, playbook_dir_path, inventory_path)


if __name__ == '__main__':
    main()