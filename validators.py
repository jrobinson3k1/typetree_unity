import os
import logging
import argparse
import re


class ValidateFolderExistsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            raise ValueError(values + " does not exist")
        setattr(namespace, self.dest, values)


class ValidateAssemblyFileExistsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        file_path = os.path.join(namespace.assembly_folder, values)
        if not os.path.isfile(file_path):
            raise ValueError("Assembly file does not exist")
        if not file_path.endswith(".dll"):
            raise ValueError("Not a valid assembly file")
        setattr(namespace, self.dest, values)


class ValidateOutputFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        dir, file_name = os.path.split(values)
        if not dir:
            dir = namespace.default_output_folder

        output_file = os.path.join(dir, file_name)
        if not os.access(os.path.dirname(output_file), os.W_OK):
            raise ValueError("Output path inaccessible")
        setattr(namespace, self.dest, output_file)


class ValidateUnityVersion(argparse.Action):
    _sem_ver_regex = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"

    def __call__(self, parser, namespace, values, option_string=None):
        # Unity sorta follows semantic versioning (Major.Minor.Patch)
        # The Patch value typical contains a letter identifier after the initial version number. Strip that out.
        match = re.search(self._sem_ver_regex, values)
        if not match:
            raise ValueError("Invalid Unity build version")

        version = match.group(0)
        if version != values:
            logging.info("Resolved Unity version from " + values + " to " + version)
        setattr(namespace, self.dest, version)
