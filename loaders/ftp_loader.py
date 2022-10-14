import argparse
from pathlib import Path
from tqdm import tqdm
import urllib.request

class FtpLoader:
    def __init__(self, 
                 address: str, 
                 login: str, 
                 password: str,
                 out_dir: Path=Path('./cache')):
        self.ftp = f"ftp://{login}:{password}@{address}"

        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def download(self, file_path: Path, progress: bool=True):
        url = f"{self.ftp}:{file_path}"
        tmp_file = self.out_dir / file_path.name

        if not tmp_file.exists():
            if progress:
                with tqdm(unit='B', 
                          unit_scale=True, 
                          unit_divisor=1024, 
                          ascii=True,
                          desc="Downloading from FTP") as t:
                    urllib.request.urlretrieve(url, tmp_file, self.__tqdm_hook(t))
            else:
                urllib.request.urlretrieve(url, tmp_file)

    @staticmethod
    def __tqdm_hook(t):
        last_b = [0]

        def update_to(b=1, bsize=1, tsize=None):
            if tsize is not None:
                t.total = tsize
            t.update((b - last_b[0]) * bsize)
            last_b[0] = b

        return update_to

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--address",
        required=True,
        help="FTP address")

    parser.add_argument(
        "-l", "--login",
        required=True,
        help="FTP login")

    parser.add_argument(
        "-p", "--password",
        required=True,
        help="FTP password")

    parser.add_argument(
        "-f", "--file_path",
        required=True,
        type=Path,
        help="FTP file path")

    parser.add_argument(
        "-o", "--out_dir",
        default="./cache",
        type=Path,
        help="Output directory [default: ./cache")

    args = parser.parse_args()
    ftp = FtpLoader(args.address, args.login, args.password, args.out_dir)
    ftp.download(args.file_path)

if __name__ == "__main__":
    main()
    
