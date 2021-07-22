#! /usr/bin/env python3
# coding: utf8

"""
File : utility.py
Author : lgbarrere
Brief : Define all constants and "tool" functions to use in other scripts
"""
from os import path
from pathlib import Path
import logging as lg


class Constants:
    """
    Brief : Constants
    """
    # Path to root folder
    __ROOT_PATH = path.dirname(path.dirname(path.dirname(__file__)))
    __DATA_FOLDER = 'data' # Name of the data folder
    __DATA_PATH = path.join(__ROOT_PATH, __DATA_FOLDER) # Path to data
    __SAVE_FOLDER = 'saves' # Name of the save folder
    __SAVE_PATH = path.join(__ROOT_PATH, __SAVE_FOLDER) # Path to saves
    __RESULT_FOLDER = 'result' # Name of the result folder
    __RESULT_PATH = path.join(__ROOT_PATH, __RESULT_FOLDER) # Path to result
    __RESULT_FILE = 'result.sol' # File to save the detailed information


    def __init__(self):
        pass


    ## Getters
    def get_root_path(self):
        """
        Brief : Get the path to the root folder of this project
        Return : Path to the root folder
        """
        return self.__ROOT_PATH


    def get_data_folder(self):
        """
        Brief : Get the name of the data folder
        Return : Name of data folder
        """
        return self.__DATA_FOLDER


    def get_data_path(self):
        """
        Brief : Get the path to the data folder
        Return : Path to the data folder
        """
        return self.__DATA_PATH


    def get_save_folder(self):
        """
        Brief : Get the name of the save folder
        Return : Name of save folder
        """
        return self.__SAVE_FOLDER


    def get_save_path(self):
        """
        Brief : Get the path to the save folder
        Return : Path too the save folder
        """
        return self.__SAVE_PATH


    def get_result_folder(self):
        """
        Brief : Get the name of the result folder
        Return : Name of result folder
        """
        return self.__RESULT_FOLDER


    def get_result_path(self):
        """
        Brief : Get the path to the result folder
        Return : Path to the result folder
        """
        return self.__RESULT_PATH


    def get_result_file(self):
        """
        Brief : Get the result file name
        Return : Result file name
        """
        return self.__RESULT_FILE


def path_tail(path_name):
    """
    Brief : Get the name of the last element (tail) in a given path
    Return : Tail of the path
    > path_name : Path from which to extract the tail
    """
    head, tail = path.split(path_name)
    return tail or path.basename(head)


def to_ilp_suffix(file):
    """
    Brief : Change the extension of the given file name by '.lpt'
    Return : Modified file name
    > file : Name of the file to change the extension
    """
    return Path(file).with_suffix('.lpt')


def lines_from_file(file_path):
    """
    Brief : Open a file from the given path to get every lines
    Return : Every lines in a list
    > file_path : Path of the file to open
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            lg.debug("Read done !")
            return lines
    except FileNotFoundError as error:
        lg.critical("The file was not found. %s", error)
    return None


def split(string, splitter_list):
    """
    Brief : Split the given string with a list of splitters
    Return : Splitted string in a list of string list
    > string : String to split
    > splitter_list : List containing the strings used to split
    """
    txt_list = []
    for i in range(len(splitter_list)-1) :
        theme_list = []
        pos1 = string.find(splitter_list[i]) + len(splitter_list[i])
        pos2 = string.find(splitter_list[i + 1])
        tmp_pos = pos1
        while pos1 < pos2 :
            if string[tmp_pos] == '\n' :
                theme_list.append(string[pos1:tmp_pos])
                pos1 = tmp_pos + 1
            tmp_pos += 1
        txt_list.append(theme_list)
    return txt_list


def build_path(path_name, option_folder = None, file_name = None):
    """
    Brief : Build the absolute path to requested folders and a file name
    Return : The path in a string
    > path_name : Path to start
    > option_folder : If given, a folder is added at the end of the path
    > file_name : If given, a file name is added at the end of the path
    (after option_folder)
    """
    complete_path = path_name
    if option_folder is not None:
        complete_path = path.join(complete_path, option_folder)
    if file_name is not None:
        complete_path = path.join(complete_path, file_name)
    return complete_path


if __name__ == '__main__':
    const = Constants()
    print(const.get_root_path())
