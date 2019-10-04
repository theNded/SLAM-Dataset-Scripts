import argparse

from os import listdir, makedirs
from os.path import exists, isfile, join, splitext
import shutil
import re


def sorted_alphanum(file_list_ordered):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(file_list_ordered, key=alphanum_key)


def get_file_list(path, rel_path, extension=None):
    if extension is None:
        file_list = [
            rel_path + f for f in listdir(path) if isfile(join(path, f))
        ]
    else:
        file_list = [
            rel_path + f for f in listdir(path)
            if isfile(join(path, f)) and splitext(f)[1] == extension
        ]
    file_list = sorted_alphanum(file_list)
    return file_list


def add_if_exists(path_dataset, folder_names):
    for folder_name in folder_names:
        if exists(join(path_dataset, folder_name)):
            return folder_name


def get_rgbd_file_lists(path_dataset):
    path_color = add_if_exists(path_dataset, ["image/", "rgb/", "color/"])
    path_depth = "depth/"

    abs_path_color = join(path_dataset, path_color)
    color_files = get_file_list(abs_path_color, path_color, ".jpg") + \
            get_file_list(abs_path_color, path_color, ".png")

    abs_path_depth = join(path_dataset, path_depth)
    depth_files = get_file_list(abs_path_depth, path_depth, ".png")
    return color_files, depth_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate association file')
    parser.add_argument('dataset', help='path to dataset')

    args = parser.parse_args()

    color_files, depth_files = get_rgbd_file_lists(args.dataset)

    assert(len(color_files) == len(depth_files))
    n = len(color_files)

    with open(join(args.dataset, 'associated.txt'), 'w') as f:
        for i in range(0, n):
            f.write('{} {} {} {}\n'.format(i, color_files[i], i, depth_files[i]))

    with open(join(args.dataset, 'rgb.txt'), 'w') as f:
        for color_file in color_files:
            f.write('{}\n'.format(color_file))

    with open(join(args.dataset, 'depth.txt'), 'w') as f:
        for depth_file in depth_files:
            f.write('{}\n'.format(depth_file))
    

    with open(join(args.dataset, 'calibration.txt'), 'w') as f:
        f.write('525.0 525.0 319.5 239.5')
