#!/usr/bin/env python3

import os
import shutil
import yaml
import time

def new_instance():
    try:
        os.system('clear')
        
        os.umask(0o000)

        # Get the latest instance number and port
        instance_dirs = [int(dir[4:]) for dir in os.listdir() if dir.startswith('odoo') and dir[4:].isdigit()]
        if not instance_dirs:
            raise FileNotFoundError("No 'odoo' instances found.")

        latest_instance = max(instance_dirs)
        latest_instance_port = 8069 + latest_instance - 1

        # Create new instance details
        new_instance_number = latest_instance + 1
        new_instance_name = f"odoo{new_instance_number}"
        new_instance_port = latest_instance_port + 1
        new_etc_directory = f"./odoo{new_instance_number}"
        print(f"Creating new instance: {new_instance_name} on port {new_instance_port}...")
        time.sleep(2)

        # Copy the template directory
        shutil.copytree('./odoo_template', new_etc_directory)

        # Load the latest yml file
        with open(f'odoo{latest_instance}.yml', 'r') as file:
            data = yaml.safe_load(file)

        # Create new service
        new_service = {
            'image': 'odoo:latest',
            'container_name': new_instance_name,
            'depends_on': ['db'],
            'ports': [f"{new_instance_port}:8069"],
            'tty': True,
            'command': '--dev=all',
            'environment': [
                'HOST=db',
                'USER=odoo',
                'PASSWORD=odoo16@2022'
            ],
            'volumes': [f'./odoo{new_instance_number}/addons:/mnt/extra-addons', f'{new_etc_directory}/etc:/etc/odoo'],
            'networks': [f'odoo{new_instance_number}-network'],
            'restart': 'on-failure:5'
        }

        # Add new service to the yml data
        data['services'][new_instance_name] = new_service

        # Add new network to the yml data
        data['networks'][f'odoo{new_instance_number}-network'] = {'name': f'odoo{new_instance_number}-network', 'driver': 'bridge'}

        # Add new network to the PostgreSQL container
        data['services']['db']['networks'].append(f'odoo{new_instance_number}-network')

        # Write the new yml data to a new file
        with open(f'odoo{new_instance_number}.yml', 'w') as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        # Set permissions for the new directories and files
        os.chmod(new_etc_directory, 0o777)  # Setting 777 permission for the new directory
        for root, dirs, files in os.walk(new_etc_directory):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o777)  # Setting 777 permission for subdirectories
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)  # Setting 777 permission for files

        input(f"New instance {new_instance_name} created, press enter to continue.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_instances():
    try:
        os.system('clear')

        # Get the number of existing instances
        instance_dirs = [dir for dir in os.listdir() if dir.startswith('odoo') and dir[4:].isdigit()]
        num_existing_instances = len(instance_dirs)

        if num_existing_instances == 0:
            input("No instances found. Please create an instance first.")
            return

        print(f"{num_existing_instances} instance(s) found.")

        desired_instances = int(input("Enter the number of instances to run: "))

        if desired_instances > num_existing_instances:
            os.system('clear')
            input("Error: The desired number of instances exceeds the existing ones. Press Enter to return to the main menu.")
            return
        else:
            # Run the specified YAML file corresponding to the desired number of instances
            os.system('clear')
            os.system(f"sudo docker-compose -f odoo{desired_instances}.yml up -d")
            time.sleep(2)

            # Show container status
            os.system('clear')
            os.system(f"sudo docker-compose -f odoo{desired_instances}.yml ps -a")
            print("")
            print("-------------------------------------------------------------------------------")
            input("Press Enter to stop and remove all containers.")

            # Stop and remove containers
            os.system('clear')
            print("Proceeding to stop and remove containers...")
            os.system(f"sudo docker-compose -f odoo{desired_instances}.yml down --remove-orphans")
            print("Stopped and removed containers. Returning to the main menu...")
            os.system('sudo chmod -R 777 .')  # Optional - to change permissions
            time.sleep(2)

    except ValueError:
        input("Invalid input. Please enter a valid number.")
    except Exception as e:
        input(f"An error occurred: {e}")


def request_sudo_permissions():
    os.system('clear')
    print("Requesting sudo permissions...")
    time.sleep(1)
    os.system('sudo echo "Sudo permissions granted"')
    print("Loading main menu...")
    time.sleep(2)
        
def main_menu():
    while True:
        os.system('clear')
        print("============ Multiple Odoo instances management system ============")
        print("1. Run desired number of Odoo instances")
        print("2. Create a new Odoo instance")
        print("0. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            run_instances()
        elif choice == "2":
            new_instance()
        elif choice == "0":
            print("Exiting the program.")
            break
        else:
            os.system('clear')
            input("Invalid choice. Press Enter to retry.")

if __name__ == "__main__":
    request_sudo_permissions() 
    main_menu()
