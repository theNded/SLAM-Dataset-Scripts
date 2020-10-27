import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')

    args = parser.parse_args()

    with open('{}/associate.txt'.format(args.path), 'r') as f:
        content = f.readlines()

    os.makedirs('{}/depth_mf'.format(args.path), exist_ok=True)
    os.makedirs('{}/color_mf'.format(args.path), exist_ok=True)
    os.makedirs('{}/mask_mf'.format(args.path), exist_ok=True)

    for i, line in enumerate(content):
        lst = line.strip().split(' ')
        color = lst[1]
        depth = lst[3]
        os.rename('{}/{}'.format(args.path, color),
                  '{}/color_mf/{:04d}.png'.format(args.path, i))
        os.rename('{}/{}'.format(args.path, depth),
                  '{}/depth_mf/{:04d}.png'.format(args.path, i))
