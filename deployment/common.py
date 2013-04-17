"""
Set of functions that are common among deployment classes.
"""

import os

from lib import util


def get_run_levels(dir_path):
    """Return sorted list of directory content

    Args:
        dir_path ( string ) : directory path

    Return:
        list or bool
    """
    try:
        contents = []
        folder_contents = sorted(os.listdir(dir_path))
        for item in folder_contents:
            item_first_chr = item.split("-")[0]
            try:
                if os.path.isdir(os.path.join(dir_path, item)) and \
                   item_first_chr.isdigit():
                    contents.append(item)
            except:
                continue

        return contents
    except OSError:
        return False


def get_executable_files(run_level_dir):
    """get executable files from a directory

    Given a directory, walk into it and return absolute path of files
    that are executable

    Args:
        run_level_dir ( string ) : directory path

    Return :
        scripts_list ( list ) : contains all executable files

    """
    scripts_list = []
    for root, dirs, files in os.walk(run_level_dir):
        for afile in files:
            file_abs_path = os.path.join(root, afile)
            if util.is_executable_file(file_abs_path):
                scripts_list.append(os.path.join(root, afile))
    return scripts_list


def get_stages(mode, levels_dir, remote_dir=""):
    """Get the stages of execution in a dict format

    Given a root directory of the stages, loop over those levels and
    extract all executable scripts based on given mode, i.e : client
    or server.

    Args:
        mode (string) : client or server
        levels_dir (string) : deployment stage root dir

    return:
        stages_dict (dict) : every key represent an execution level,
        the value of that key is list of all executable scripts in
        that level.

    """
    stages_dict = {}
    levels = get_run_levels(levels_dir)
    if levels:
        for level in levels:
            abs_path = os.path.join(levels_dir, level)
            if level.startswith("0-"):
                tmp_exec_files = get_executable_files(abs_path)
                if tmp_exec_files:
                    stages_dict[level] = get_executable_files(abs_path)
            else:
                abs_path_w_mode = os.path.join(abs_path, mode)
                stages_dict[level] = get_executable_files(abs_path_w_mode)

    for key, value in stages_dict.iteritems():
        stages_dict[key] = [x.replace(levels_dir, remote_dir, 1)
                            for x in value]

    return stages_dict
