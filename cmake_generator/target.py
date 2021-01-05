import logging
from . import constants

LOG = logging.getLogger(__name__)

__all__ = ["Project", "Application", "Library"]

class Project(object):
    def __init__(self, name, version, install=False, custom_install=None):

        if not isinstance(name, str):
            raise TypeError(f"name attribute must be set to an instance of str")
        else:
            if " " in name:
                raise ValueError("name attribute can't contain spaces")

        if not isinstance(version, str):
            raise TypeError(f"version attribute must be set to an instance of str")

        if not isinstance(install, bool):
            raise TypeError(f"install attribute must be set to an instance of bool")

        if custom_install is not None and not isinstance(custom_install, str):
            raise TypeError(f"custom_install attribute must be set to an instance of str")

        self.name = name
        self.version = version
        self.custom_install = custom_install
        self.install = install

        self.targets = []

    def add_targets(self, *targets):
        self.targets.extend(targets)

    def gen_project(self):

        text = f"cmake_minimum_required(VERSION 3.13...3.16 FATAL_ERROR)\n"
        text += f"project({self.name} VERSION {self.version} LANGUAGES CXX)\n\n"

        if self.custom_install is not None:
            text += "# Use this snippet *after* PROJECT(xxx) to change the default installation directory\n"
            text += "IF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)\n"
            text += f"    SET(CMAKE_INSTALL_PREFIX {self.custom_install} CACHE PATH comment FORCE)\n"
            text += "ENDIF(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)\n\n"

        text += "#Make sure that custom modules like FindRapidJSON are found\n" \
                "list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_SOURCE_DIR}/cmake)\n"

        # TODO add dependencies

        for target in self.targets:
            text += target.gen_target()

        if self.install:
            text += self.gen_install()

        return text

    def gen_install(self):
        text = f"##############################################\n"
        text += f"# Installation instructions\n"
        text += f"\n"
        text += f"include(GNUInstallDirs)\n"
        text += f"set(INSTALL_CONFIGDIR ${{CMAKE_INSTALL_LIBDIR}}/cmake/{self.name})\n"
        text += f"\n"
        text += f"install(TARGETS {self.name}\n"
        text += f"    EXPORT {self.name}_targets\n"
        text += f"    LIBRARY DESTINATION ${{CMAKE_INSTALL_LIBDIR}}\n"
        text += f"    ARCHIVE DESTINATION ${{CMAKE_INSTALL_LIBDIR}}\n"
        text += f")\n"
        text += f"\n"
        text += f"#This is required so that the exported target has the name JSONUtils and not jsonutils\n"
        text += f"set_target_properties({self.name} PROPERTIES EXPORT_NAME {self.name})\n"
        text += f"\n"
        text += f"install(DIRECTORY include/ DESTINATION ${{CMAKE_INSTALL_INCLUDEDIR}})\n"
        text += f"\n"
        text += f"#Export the targets to a script\n"
        text += f"install(EXPORT ${{{self.name}}}_targets\n"
        text += f"    FILE\n"
        text += f"        {self.name}Targets.cmake\n"
        text += f"    NAMESPACE\n"
        text += f"        {self.name}::\n"
        text += f"    DESTINATION\n"
        text += f"        ${{INSTALL_CONFIGDIR}}\n"
        text += f")\n"
        text += f"\n"
        text += f"#Create a ConfigVersion.cmake file\n"
        text += f"include(CMakePackageConfigHelpers)\n"
        text += f"write_basic_package_version_file(\n"
        text += f"    ${{CMAKE_CURRENT_BINARY_DIR}}/{self.name}ConfigVersion.cmake\n"
        text += f"    VERSION ${{PROJECT_VERSION}}\n"
        text += f"    COMPATIBILITY AnyNewerVersion\n"
        text += f")\n"
        text += f"\n"
        text += f"configure_package_config_file(${{CMAKE_CURRENT_LIST_DIR}}/cmake/{self.name}Config.cmake.in\n"
        text += f"    ${{CMAKE_CURRENT_BINARY_DIR}}/{self.name}Config.cmake\n"
        text += f"    INSTALL_DESTINATION ${{INSTALL_CONFIGDIR}}\n"
        text += f")\n"
        text += f"\n"
        text += f"#Install the config, configversion and custom find modules\n"
        text += f"install(FILES\n"
        text += f"    ${{CMAKE_CURRENT_LIST_DIR}}/cmake/FindRapidJSON.cmake\n"
        text += f"    ${{CMAKE_CURRENT_BINARY_DIR}}/{self.name}Config.cmake\n"
        text += f"    ${{CMAKE_CURRENT_BINARY_DIR}}/{self.name}ConfigVersion.cmake\n"
        text += "    DESTINATION ${{INSTALL_CONFIGDIR}}\n"
        text += ")\n"
        text += "\n"
        text += "##############################################\n"
        text += "## Exporting from the build tree\n"
        text += "configure_file(${{CMAKE_CURRENT_LIST_DIR}}/cmake/FindRapidJSON.cmake\n"
        text += "    ${{CMAKE_CURRENT_BINARY_DIR}}/FindRapidJSON.cmake\n"
        text += "    COPYONLY)\n"
        text += "\n"
        text += f"export(EXPORT {self.name}_targets\n"
        text += f"    FILE ${{CMAKE_CURRENT_BINARY_DIR}}/{self.name}Targets.cmake\n"
        text += f"    NAMESPACE {self.name}::)\n"
        text += f"\n"
        text += f"#Register package in user's package registry\n"
        text += f"export(PACKAGE {self.name})\n\n"

        return text

    def write(self):
        filename = constants.cmake_filename

        stringify = self.gen_project()

        obj = open(filename, "w")
        obj.write(stringify)
        obj.close()

class Target(object):
    def __init__(self, name):
        self.name = name
        self.headers = []
        self.sources = []

    def add_sources(self, sources):
        self.sources.extend(sources)
        
    def add_headers(self, headers):
        self.headers.extend(headers)

class Application(Target):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Library(Target):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def gen_target(self):
        text = f"add_library({self.name} SHARED "")\n"
        text += f"\n"
        text += f"target_sources({self.name}\n"
        text += f"    PRIVATE\n"
        for s in self.sources:
            text += f"        {s}\n"

        text += f"    PUBLIC\n"
        for h in self.headers:
            text += f'        "$<BUILD_INTERFACE:${{CMAKE_CURRENT_LIST_DIR}}/{h}>"\n'

        text += f"    )\n"
        text += f"\n"
        text += f"set_target_properties({self.name} PROPERTIES PUBLIC_HEADER\n"

        tmp_list = []
        for h in self.headers:
            tmp_list.append(f"${{CMAKE_CURRENT_LIST_DIR}}/{h}")
        text += f'        "{";".join(tmp_list)}"\n'

        text += f"        )\n"
        text += f"\n"
        text += f"#target_link_libraries(toto_shared PUBLIC lib) # en modern cmake il faut toujours definir ce quon veut shared ou pas\n"
        text += f"\n"
        text += f"# when used as a client, the relative path is different with this. not needed if identical to source build\n"
        text += f"target_include_directories({self.name}\n"
        text += f"    PUBLIC\n"
        text += f"        $<BUILD_INTERFACE:${{{self.name}_SOURCE_DIR}}/include>\n"
        text += f"        $<INSTALL_INTERFACE:${{CMAKE_INSTALL_INCLUDEDIR}}>\n"
        text += f"    )\n"
        text += f"\n"
        text += f"add_library({self.name}::{self.name} ALIAS {self.name})\n"
        text += f"# notion dalias. si je fait pas ça, le client doit modifier le target include diretories et modifier le target link de lexecutable\n"
        text += f"# avec un alias cmake cree un wrapper et lapp cliente avec le nom alias et il va rajouter les flags tout seul\n"
        text += f"# il faut utiliser ça par defaut pour que ce soit plus simple pour le client\n"

        return text