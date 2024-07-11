import os
import subprocess
import argparse
from simple_term_menu import TerminalMenu
from colorama import init,Fore,Back, Style


init(autoreset=True)


## variables
project_name = None
project_directory = None
project_addons = ()
project_type = None
project_core_app_name = "core"


PROJECT_TYPES = ["[d] default","[r] django rest framework", "[n] django ninja"]
PROJECT_TYPES_INSTALS = ["_","djangorestframework","django-ninja"]
PROJECT_ADDONS = ["none","django auth","django all-auth","htmx","tailwind","bootstrap"]


def main_template_selection():


    cont = False

    terminal_menu = TerminalMenu(PROJECT_TYPES)
    menu_entry_index = -1
    while not cont:
        menu_entry_index = terminal_menu.show()

        print(f"Selected is {PROJECT_TYPES[menu_entry_index]} ")
        are_you_sure = input("Continue with selection [Y]es or [N]o: ")
        cont = are_you_sure.lower().startswith('y')

    return menu_entry_index

            
def select_project_addons():
    terminal_menu = TerminalMenu(
        PROJECT_ADDONS,
        multi_select=True,
        show_multi_select_hint=True
    )

    cont = False
    select_addons_indices = ()
    while not cont:
        selected_addons_indices = terminal_menu.show()
        if 0 in select_addons_indices:
            are_you_sure = input("Continue with selection [Y]es or [N]o: ")
            cont = are_you_sure.lower().startswith('y')
            select_addons_indices = ()
        else:
            print("You have chosen to add")
            for ent in terminal_menu.chosen_menu_entries:
                print("> ",ent)

            are_you_sure = input("Continue with selection [Y]es or [N]o: ")
            cont = are_you_sure.lower().startswith('y')
    
    print(selected_addons_indices)
    return select_addons_indices


def create_django_project(project_name,project_directory,project_type,django_version=None):
    
    # install django
    print(f"{Fore.GREEN}Installing django{Fore.BLACK}")

    subprocess.run(f"python -m pip install Django")

    print(f"{Fore.GREEN}Creating django project{Fore.BLACK}")
    
    create_prject_command = f"django-admin startproject {project_name}"
    if project_directory != None:
        pass




def main(args=None):
    
    global project_name, project_directory

    parser = argparse.ArgumentParser(description="Django Project Initializer")
    parser.add_argument('--pname',type=str,help="project name")
    parser.add_argument("--pdir", type=str,help="project directory")

    parsed_args = parser.parse_args(args)

    project_name = parsed_args.pname
    project_directory = parsed_args.pdir

    print(os.getcwd())
    if project_name == None:
        project_name = input(f"{Fore.GREEN}> --pname {Fore.WHITE} not set please enter a name for your project: ")

    print("Please Choose a django project type to initialize")

    project_type = main_template_selection() 
    project_addons = select_project_addons()

    print(f"initializing {project_name} at {project_directory}")

    
    # initializing project

    


if __name__ == "__main__":
    main(None)