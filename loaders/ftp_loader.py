import os
import argparse
from pathlib import Path
from tqdm import tqdm
import ftplib
import yaml

class TQDMWrapperForFTP:
    def __init__(self, t, rest=0, total_size=None):
        self.t = t
        self.t.update(rest)
        self.t.total = total_size

    def upload_callback(self, buf):
        self.t.update(len(buf))

    def download_callback(self, buf, write_foo):
        self.t.update(len(buf))
        write_foo(buf)


class FtpLoader:
    def __init__(self, 
                 address: str, 
                 login: str, 
                 password: str):

        self.ftp = ftplib.FTP(address, login, password)
        self.ftp.encoding = "utf-8"

    def download(self, file_path: Path, out_dir: Path):
        self.ftp.sendcmd("TYPE i") 
        file_size = self.ftp.size(str(file_path))
        self.ftp.sendcmd("TYPE A") 

        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir/file_path.name

        rest = 0
        if out_path.exists():
            rest = os.stat(out_path).st_size

        with open(out_path, "ab") as file:
            with tqdm(unit='B',
                      unit_scale=True,
                      unit_divisor=1024,
                      ascii=True,
                      desc="Download from FTP") as t:
                tqdm_wrapper = TQDMWrapperForFTP(t=t, rest=rest, total_size=file_size)
                callback = lambda block: tqdm_wrapper.download_callback(block, file.write)
                self.ftp.retrbinary(f"RETR {file_path}", callback=callback, rest=rest)

    def upload(self, file_path: Path, ftp_dir: Path):
        self.__ftp_mkdir(ftp_dir)
        file_size = os.stat(file_path).st_size
        self.ftp.cwd(str(ftp_dir))
        with open(file_path, "rb") as file:
            with tqdm(unit='B',
                      unit_scale=True,
                      unit_divisor=1024,
                      ascii=True,
                      desc="Upload to FTP") as t:
                tqdm_wrapper = TQDMWrapperForFTP(t=t, total_size=file_size)
                self.ftp.storbinary(f"STOR {file_path.name}", file, callback=tqdm_wrapper.upload_callback)

    def __ftp_mkdir(self, dir_path: Path):
        tree = []

        while len(str(dir_path)) > 1:
            tree.append(dir_path)
            dir_path = dir_path.parent

        for d in tree[::-1]:
            try:
                self.ftp.cwd(str(d))
            except:
                self.ftp.mkd(str(d))

# config example:
# server:
#   address: <name>
#   login: <login>
#   passowrd: <password>
def read_config(path: Path):
    with open(path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return {'address' : config['server']['address'],
            'login' : config['server']['login'],
            'password' : config['server']['password']}

def main():
    config_path = Path('./.ftp_loader_config.yaml')
    config = None
    if config_path.exists():
        config = read_config(config_path)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a", "--address",
        required=config is None,
        help="FTP address")

    parser.add_argument(
        "-l", "--login",
        required=config is None,
        help="FTP login")

    parser.add_argument(
        "-p", "--password",
        required=config is None,
        help="FTP password")

    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands", dest='command'
    )
    download_parser = subparsers.add_parser(
        "download", aliases=["d"], help="Download file from ftp"
    )
    download_parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="FTP file path")

    download_parser.add_argument(
        "-o", "--output",
        default="./cache",
        type=Path,
        help="Output directory [default: ./cache")

    upload_parser = subparsers.add_parser(
        "upload", aliases=["u"], help="Upload file to ftp"
    )
    upload_parser.add_argument(
        "-i", "--input",
        required=True,
        type=Path,
        help="File path")

    upload_parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output directory ot FTP")

    args = parser.parse_args()

    address = args.address if args.address else config['address']
    login = args.login if args.login else config['login']
    password = args.password if args.password else config['password']

    ftp = FtpLoader(address, login, password)
    if not args.command:
        parser.print_usage()
    elif args.command in ["download", "d"]:
        ftp.download(args.input, args.output)
    elif args.command in ["upload", "u"]:
        ftp.upload(args.input, args.output)

if __name__ == "__main__":
    main()
    
