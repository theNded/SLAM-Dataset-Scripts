import os
import shutil
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    args = parser.parse_args()

    with open('{}/camera-intrinsics.txt'.format(args.path)) as f:
        content = f.readlines()
    print(content)
    line0 = list(map(float, content[0].strip().split(' ')))
    line1 = list(map(float, content[1].strip().split(' ')))
    fx, cx = line0[0], line0[2]
    fy, cy = line1[1], line1[2]
    with open('{}/cal.txt'.format(args.path), 'w') as f:
        f.write('{} {} {} {}\n'.format(fx, fy, cx, cy))

    fnames = sorted(os.listdir('{}/seq-01'.format(args.path)))

    fnames = list(
        filter(lambda x: os.path.isfile('{}/seq-01/{}'.format(args.path, x)),
               fnames))
    print(fnames)
    fname_colors = list(filter(lambda x: x.split('.')[-2] == 'color', fnames))
    fname_depths = list(filter(lambda x: x.split('.')[-2] == 'depth', fnames))
    fname_poses = list(filter(lambda x: x.split('.')[-2] == 'pose', fnames))

    print(len(fname_colors))
    print(len(fname_depths))
    print(len(fname_poses))

    os.makedirs('{}/seq-01/color'.format(args.path), exist_ok=True)
    os.makedirs('{}/seq-01/depth'.format(args.path), exist_ok=True)
    os.makedirs('{}/seq-01/pose'.format(args.path), exist_ok=True)

    for i, data in enumerate(zip(fname_colors, fname_depths, fname_poses)):
        color, depth, pose = data
        os.rename('{}/seq-01/{}'.format(args.path, color),
                  '{}/seq-01/color/{:04d}.png'.format(args.path, i))
        os.rename('{}/seq-01/{}'.format(args.path, depth),
                  '{}/seq-01/depth/{:04d}.png'.format(args.path, i))
        os.rename('{}/seq-01/{}'.format(args.path, pose),
                  '{}/seq-01/pose/{:04d}.txt'.format(args.path, i))
