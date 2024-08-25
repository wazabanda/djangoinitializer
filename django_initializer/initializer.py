from typing import List,Dict,Any
import os
import subprocess
import argparse
import requests
from simple_term_menu import TerminalMenu
from colorama import init,Fore,Back, Style
from .code_helper import modify_or_add_setting, get_file_values
import shutil
from importlib import resources
from pathlib import Path

init(autoreset=True)

# TODO: implement drf imlement dninja  

## variables
project_name = None
project_directory = None
project_addons = ()
project_type = None
project_core_app_name = "core"


# PROJECT_TYPES = ["[d] default","[r] django rest framework", "[n] django ninja"]
PROJECT_TYPES = ["[d] default", "[n] django ninja"]
PROJECT_TYPES_INSTALS = ["_","djangorestframework","django-ninja"]
PROJECT_ADDONS = ["none","django all-auth","htmx","tailwind (CDN)","alpine 3.x.x (CDN)","crispy_tailwind"]

template_path = resources.files("django_initializer").joinpath('templates')

def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)


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
    
     # print(selected_addons_indices)
    return terminal_menu.chosen_menu_entries


def create_base_template(project_name,templates,addons,addon_statements):
    
    content = [] 
    content
    template_path = resources.files("django_initializer").joinpath('templates')
    base_template_file = template_path.joinpath('global').joinpath('base.html')
    with base_template_file.open('r') as f:
        content = f.readlines()

    SCRIPTS_IDENTIFIER = content.index( "<!--scripts-->\n")
    HEAD_IDENTIFIER = content.index("<!--head-->\n")

    for cont in addon_statements['head']:
        content.insert(HEAD_IDENTIFIER,cont)
    

    for cont in addon_statements['scripts']:
        content.insert(SCRIPTS_IDENTIFIER,cont)


    global_path = os.path.join(templates,'base')
    create_directory(global_path)
    
    txt = template_path.joinpath('global').joinpath('site_base.html').read_text()

    with open(os.path.join(templates,'base','site_base.html'),'w') as f:
        f.write(txt)

    
    with open(os.path.join(templates,'base','base.html'),'w') as f:
        f.writelines(content)

    # print(content)

    
        
    
def create_static_folders(project_name,project_directory,settings_path,create_core=True):

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
    templates_sub_dirs = ['base']
    
    if create_core:
        templates_sub_dirs.append("core")

    dirs = {}
    print(project_directory) 
    for folder in folder_to_create:
        path = os.path.join(project_directory,folder)
        dirs[folder] = path 
        # static_path = path
        create_directory(path)
        # os.mkdir(path)

    # print(static_path)
        
    for folder in static_sub_dirs:
        create_directory(os.path.join(dirs['staticfiles'],folder))
    
    for folder in templates_sub_dirs:
        create_directory(os.path.join(dirs['templates'],folder))

    with open(settings_path,'a') as settings:
        settings.write(to_append)
    
    print(dirs)
    return dirs


def add_crispy_forms(settings_path):
    # Install crispy forms
    print("Installing Crispy Dependencies")
    cmd = "pip install django-crispy-forms crispy-tailwind".split()
    subprocess.run(cmd)
    
    installed_apps:List[Any] = get_file_values(settings_path,"INSTALLED_APPS")
    installed_apps.append('crispy_forms')
    installed_apps.append('crispy_tailwind')
    modify_or_add_setting(settings_path,"INSTALLED_APPS",installed_apps)
    modify_or_add_setting(settings_path,"CRISPY_ALLOWED_TEMPLATE_PACKS","tailwind")
    modify_or_add_setting(settings_path,"CRISPY_TEMPLATE_PACK",'tailwind')



def get_htmx(project_name,project_directory):
    
    HTMX_UNPKG_URL = "https://unpkg.com/htmx.org/dist/htmx.min.js" # todo move to configs
    print(f"{Fore.YELLOW} {Style.BRIGHT} Adding HTMX You have amazing tastes!! {Fore.RESET} {Style.RESET_ALL}")
    contents = requests.get(HTMX_UNPKG_URL).text

    path = os.path.join(project_directory,"staticfiles",'js','htmx.min.js')
    with open(path,'w') as f:
        f.write(contents)

    return path


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
    
    create_core = False
    # create_core_app_prompt = input(f"{Fore.GREEN}Do You want to create a core app (default)[Y]es or [N]o: {Fore.WHITE}")

    settings_path = os.path.join(working_directory,project_name,'settings.py')
    dirs = create_static_folders(project_name,working_directory,settings_path,create_core)

    dirs['settings'] = settings_path
    dirs['working_path'] = working_directory   
    # if create_core_app_prompt in ["\n",''] or create_core_app_prompt.lower().startswith("y"):
    print(f"{Fore.GREEN}Creating core app{Fore.WHITE}")
    command = "python manage.py startapp core".split()
    create_core = True
    subprocess.run(command,cwd=working_directory)

    installed_apps:List[Any] = get_file_values(settings_path,"INSTALLED_APPS")
    installed_apps.append('core')
    modify_or_add_setting(settings_path,"INSTALLED_APPS",installed_apps)
    dirs['core_path'] = os.path.join(working_directory,'core')
    dirs['main_app_path'] = os.path.join(working_directory,project_name)
    return dirs 
    

 
def create_django_rest_project():
    pass


def create_django_ninja_project(app_paths,proj_name):

    print(f"{Fore.GREEN}Addin Django Ninja to your project")
    django_ninja_api_file = template_path.joinpath('django-ninja').joinpath("api.py")
    django_ninja_api_auth = template_path.joinpath('django-ninja').joinpath("api_auth.py")
    django_ninja_api_models = template_path.joinpath('django-ninja').joinpath("models.py")
    django_ninja_core_api = template_path.joinpath('django-ninja').joinpath("core").joinpath("api.py")
    django_ninja_urls = template_path.joinpath('django-ninja').joinpath("urls.py")
    
    cmd = "pip install django-ninja".split()
    subprocess.run(cmd)
    
    with open(os.path.join(app_paths['core_path'],'models.py'),'a') as f:
        model_file = open(str(django_ninja_api_models),'r')
        f.writelines(model_file.readlines())
        model_file.close()

     
    shutil.copy(str(django_ninja_api_file),os.path.join(app_paths['main_app_path'],'api.py'))
    shutil.copy(str(django_ninja_api_auth),os.path.join(app_paths['main_app_path'],'api_auth.py'))
    shutil.copy(str(django_ninja_urls),os.path.join(app_paths['main_app_path'],'urls.py'))
    shutil.copy(str(django_ninja_core_api),os.path.join(app_paths['core_path'],'api.py'))


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
    project_addons = []
    project_type = main_template_selection() 
    project_addons = select_project_addons()

    print(f"initializing {project_name} at {project_directory}")

    # create the project
    dirs:Dict[str,str] = create_django_project(project_name,project_directory,project_type)
    print(f"Including addons to project")
    # print(project_addons)
    static_statements = {
        "head":[],
        "scripts":[],
    }
    
    # if project_type == 1:
    #     create_django_rest_project()
    if project_type == 1:
        create_django_ninja_project(dirs,project_name)

    print(project_addons)
    for index in project_addons:
        print(f"> Adding {index}")
        # This following part is bad, make the configuration better going forward when everything works
        if index.startswith('htmx'):
            get_htmx(project_name,dirs['working_path'])
            static_statements["head"] += ["\n<script src=\"{% static 'js/htmx.min.js' %}\"></script>"]
        elif index.startswith("tailwind"):
            static_statements["head"] += ["\n<script src='https://cdn.tailwindcss.com'></script>"]
        elif index.startswith("alpine"):
            static_statements["head"] += ["\n<script defer src='https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'></script>"]
        elif index.startswith('crispy'):
            add_crispy_forms(dirs['settings'])
    
    create_base_template(project_name,dirs['templates'],project_addons,static_statements)
    

    shutil.copy(str(template_path.joinpath("makefile")),os.path.join(dirs['working_path'],'makefile'))
    
    print(f"Project created, cd into {dirs['working_path']} and run{Style.BRIGHT}{Fore.GREEN} \npython manage.py makemigrations\npython manage.py migrate or make migrations{Fore.RESET} {Style.RESET_ALL}")

    # initializing project

    


if __name__ == "__main__":
    main(None)
