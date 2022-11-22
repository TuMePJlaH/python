import argparse
import json
import os
import yadisk
from pathlib import Path
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

class YaDiskLoader:
    def __init__(self, token: Path=Path("./token.json")):
        with open(token, 'r') as json_file:
            token_data = json.load(json_file)
        self.y = yadisk.YaDisk(token=token_data['token'])

    def mkdir(self, dir_path: Path, parent: bool=True) -> None:
        if not parent:
            self.y.mkdir(dir_path)
            return

        tree = []
        loc_dir_path = dir_path
        while len(str(loc_dir_path)) > 1:
            tree.append(loc_dir_path)
            loc_dir_path = loc_dir_path.parent

        for d in tree[::-1]:
            try:
                _ = list(self.y.listdir(d))
            except yadisk.exceptions.PathNotFoundError as e:
                self.y.mkdir(d)

    def upload(self, input_path: Path, output_dir: Path, mkdir: bool=True) -> None:
        self.mkdir(output_dir)
        file_size = os.stat(input_path).st_size
        with open(input_path, "rb") as f:
            with tqdm(total=file_size, 
                      unit="B", 
                      unit_scale=True, 
                      unit_divisor=1024, 
                      ascii=True,
                      desc="Uploading to Yandex.Disk") as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                self.y.upload(wrapped_file, output_dir/input_path.name)

def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        default="./token.json",
        type=Path,
        help="Token path [default: ./token.json]")

    parser.add_argument(
        "-f", "--file_path",
        required=True,
        type=Path,
        help="Path to file for upload")

    parser.add_argument(
        "-o", "--out_dir",
        default="/",
        type=Path,
        help="Yandex Disk dir")
    return parser.parse_args()

def main():
    args = args_parse()
    ya_disk = YaDiskLoader(args.token)
    ya_disk.upload(args.file_path, args.out_dir)

if __name__ == "__main__":
    main()
    
