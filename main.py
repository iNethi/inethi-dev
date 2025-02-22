import sys
import ansible_runner
import pathlib
import yaml


def my_status_handler(data, runner_config):
    print('Status...')
    print(data['status'])


def my_event_handler(data):
    if data.get('event_data'):
        event_data = data['event_data']
        if event_data.get('name'):
            print(event_data['name'])


def write_to_inventory(ip, user, auth_type, auth_value, inventory_path):
    with open(inventory_path, 'w') as f:
        f.write("[localserver]\n")
        if auth_type == 'password':
            f.write(f"{ip} ansible_user='{user}' ansible_password='{auth_value}' "
                    f"ansible_ssh_common_args='-o StrictHostKeyChecking=no' ansible_become_pass='{auth_value}'\n")
        elif auth_type == 'key':
            f.write(f"{ip} ansible_user='{user}' ansible_ssh_private_key_file='{auth_value}' "
                    f"ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")


def save_ip_to_config(ip, config_path):
    with open(config_path, 'w') as f:
        yaml.dump({'ip_address': ip}, f)


def run_playbook(playbook_name, playbook_dir_path, inventory_path):
    playbook_path = f"{playbook_dir_path}/{playbook_name}.yml"
    r = ansible_runner.run(private_data_dir="./", playbook=playbook_path, inventory=inventory_path,
                           status_handler=my_status_handler, quiet=False, event_handler=my_event_handler)

    # Check if playbook run was successful
    if r.rc != 0:
        print(f"Error running playbook: {playbook_name}")
        sys.exit(1)


def main():
    abs_path = pathlib.Path(__file__).parent.resolve()
    choices = ['azuracast', 'jellyfin', 'keycloak', 'kiwix', 'moodle', 'nextcloud', 'radiusdesk', 'splash-screen', 'wordpress']
    # choices = ['dnsmasq', 'jellyfin', 'keycloak', 'nextcloud', 'splash-screen', 'radiusdesk', 'wordpress']
    traefik = 'traefik'
    ap_monitor = 'ap_monitor'
    test_server = "test_server_connection"
    system_requirements = "system_requirements"
    playbook_dir_path = f"{abs_path}/playbooks"
    inventory_path = f"{abs_path}/playbooks/inventory"
    config_path = f"{abs_path}/playbooks/config.yml"

    # Prompt user for IP, username, and password
    ip = input("Enter your IP address: ")
    user = input("Enter your username: ")

    auth_type = input("Are you using password or key-based authentication? (password/key): ").strip().lower()
    if auth_type == 'password':
        password = input("Enter your password: ")
        auth_value = password
    elif auth_type == 'key':
        key_path = input("Enter the absolute path to your SSH key: ")
        auth_value = key_path
    else:
        print("Invalid authentication type. Exiting.")
        sys.exit(1)
    # Write to variables to file
    write_to_inventory(ip, user, auth_type, auth_value, inventory_path)
    save_ip_to_config(ip, config_path)

    skip_setup = input(
        "Have you run the builder successfully before and want to skip system setup? (y/n): ").strip().lower()

    # Run initial playbooks only if the user does not want to skip setup
    if skip_setup != 'y':
        run_playbook(test_server, playbook_dir_path, inventory_path)
        run_playbook(system_requirements, playbook_dir_path, inventory_path)
        run_playbook(traefik, playbook_dir_path, inventory_path)

    # Prompt user to select services to install
    print("Select services to install:")
    for idx, choice in enumerate(choices, 1):
        print(f"{idx}. {choice}")

    while True:
        try:
            selected_indexes = input("Enter the numbers of the services you want to install (comma-separated): ").split(
                ',')
            selected_services = [choices[int(idx) - 1] for idx in selected_indexes]
            break
        except IndexError:
            print("Error: One or more of the service numbers you provided are out of range. Please try again.")
        except ValueError:
            print(
                "Error: Invalid input detected. Please provide a comma-separated list of service numbers in base 10 "
                "format.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Please try again.")

        # Run playbooks for selected services
    for service in selected_services:
        run_playbook(service, playbook_dir_path, inventory_path)


if __name__ == '__main__':
    main()
