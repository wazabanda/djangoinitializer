import os
import subprocess
import argparse
import requests
from simple_term_menu import TerminalMenu
from colorama import init,Fore,Back, Style
from .code_helper import modify_or_add_setting, get_file_values

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
    return selected_addons_indices


def create_static_folders(project_name,project_directory,settings_path):

    to_append = """

import os
STATICFILES_DIRS = [
    BASE_DIR/"staticfiles",
]

STATIC_URL = "/static/"
STATIC_ROOT = "static/"
MEDIA_ROOT = BASE_DIR/'media/'
MEDIA_URL = '/media/'

    """

    folder_to_create = ["staticfiles","static","media","templates"] # todo move to config
    static_sub_dirs = ['js','css','img'] # todo move to config

    static_path = ""
    for folder in folder_to_create:
        path = os.path.join(project_directory,folder)
        if folder == "static":
            static_path = path
        os.mkdir(path)

    print(static_path)
        
    for folder in static_sub_dirs:
        os.mkdir(os.path.join(static_path,folder))

    with open(settings_path,'a') as settings:
        settings.write(to_append)
    
def get_htmx(project_name,project_directory):
    
    HTMX_UNPKG_URL = "https://unpkg.com/htmx.org/dist/htmx.min.js" # todo move to configs
    print(f"f{Fore.YELLOW} {Style.BRIGHT} Adding HTMX You have amazing tastes!! {Fore.RESET} {Style.RESET_ALL}")
    contents = requests.get(HTMX_UNPKG_URL).text

    path = os.path.join(project_directory,"static",'js','htmx.min.js')
    with open(path,'w') as f:
        f.write(contents)
    



def create_django_project(project_name,project_directory,project_type,django_version=None):
    
    working_directory = ""
    # install django
    print(f"{Fore.GREEN}Installing django{Fore.BLACK}")

    subprocess.run(["python", "-m", "pip", "install", "Django"])

    print(f"{Fore.GREEN}Creating django project{Fore.BLACK}")
    
    create_project_command = f"django-admin startproject {project_name}"
    if project_directory != None:
        create_project_command += f" {project_directory}"
        working_directory = project_directory

        if working_directory == '.':
            working_directory = os.getcwd()
    else:
        working_directory = os.path.join(".",project_name)


    subprocess.run(create_project_command.split())

    print(f"Project is in {working_directory}")

    create_core_app_prompt = input(f"{Fore.GREEN}Do You want to create a core app (default)[Y]es or [N]o: {Fore.WHITE}")
    if create_core_app_prompt in ["\n",''] or create_core_app_prompt.lower().startswith("y"):
        command = "python manage.py startapp core".split()
        subprocess.run(command,cwd=working_directory)
        
        settings_path = os.path.join(working_directory,project_name,'settings.py')

        installed_apps = get_file_values(settings_path,"INSTALLED_APPS")
        installed_apps.append('core')
        modify_or_add_setting(settings_path,"INSTALLED_APPS",installed_apps)

    create_static_folders(project_name,working_directory,settings_path)
    
    return working_directory,settings_path
    

    


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

    # create the project
    project_directory = create_django_project(project_name,project_directory,project_type)
    print(f"Including addons to project")
    
    print(project_addons)
    for index in project_addons:
        print(f"> Adding {PROJECT_ADDONS[index]}")
        if PROJECT_ADDONS[index] == 'htmx':
            get_htmx(project_name,project_directory[0])
    # initializing project

    


if __name__ == "__main__":
    main(None)
