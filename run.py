import subprocess
import logging

from pathlib import Path
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

from clients.googledrive_client import GoogleDriveClient


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--input_folder',
                        type=str,
                        default='./tests')
    parser.add_argument('--output_folder',
                        type=str,
                        default='./outputs')
    parser.add_argument('--ij_exe',
                        type=str,
                        default='C:\\Users\\chetho\\Downloads\\fiji-win32\\Fiji.app\\ImageJ-win32.exe')
    parser.add_argument('--ij_template',
                        type=str,
                        default='./templates/imagej_macro_template.ijm')
    return parser.parse_args()


def get_files(path, googledrive_client: GoogleDriveClient):
    if isinstance(path, Path) and path.exists():
        logging.info('Get files from local machine.')
        return sorted(list(path.glob('**/*')))
    logging.info('Get files from google drive.')
    return googledrive_client.list_files(path)


def get_file_pairs(list_):
    res = []
    i = 0
    while i + 2 <= len(list_):
        res.append([list_[i], list_[i+1]])
        i += 2
    return res


def run(ij_template, out_dir, file1, file2, client: GoogleDriveClient):
    if isinstance(file1, Path) and isinstance(file2, Path):
        _run(ij_template, out_dir, file1, file2)
    else:
        file1 = client.download(file1['name'], file1['id'])
        file2 = client.download(file2['name'], file2['id'])
        if file1 and file2:
            _run(ij_template, out_dir, file1, file2)


def _run(ij_template, out_dir, file1, file2):
    command = [
        args.ij_exe,
        '--headless',
        '--console',
        '-macro',
        ij_template,
        f'{file1} {file2} {out_dir}'
    ]

    try:
        subprocess.check_output(command)
        logging.info(f'Process {ij_template} with {file1} and {file2}')
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    output_folder = Path(args.output_folder)        
    output_folder.mkdir(exist_ok=True)

    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        client = GoogleDriveClient()
    else:
        client = None

    files = get_files(input_folder, client)
    file_pairs = get_file_pairs(files)

    for pair in file_pairs:
        run(args.ij_template, output_folder, pair[0], pair[1], client)

    # tasks = []
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     for pair in file_pairs:
    #         tasks.append(executor.submit(run, args.ij_template, output_folder, pair[0], pair[1], client))

    # for t in tasks:
    #     t.result()

    
