from pathlib import Path

import requests
import threading
import multiprocessing
import argparse
import os
import time
import asyncio

final_async = 0.0
final_threading = 0.0
final_multiprocessing = 0.0

data_images = []
with open("images.txt", "r") as images:
    for image in images.readlines():
        data_images.append(image.strip())

image_path = Path("./images/")


def download_image(url):
    start_time = time.time()
    response = requests.get(url, stream=True)
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f'Downloading {filename} has finished at {end_time:.2f} seconds')


async def download_image_async(url):
    start_time = time.time()
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"stream": True})
    filename = image_path.joinpath(os.path.basename(url))
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Downloading {filename} has finished at {end_time:.2f} seconds")


def download_images_threading(urls):
    start_time = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time() - start_time
    print(f"Downloading has finished at {end_time:.2f} seconds")


def download_images_multiprocessing(urls):
    start_time = time.time()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    end_time = time.time() - start_time
    print(f"Downloading has finished at {end_time:.2f} seconds")


async def download_images_asyncio(urls):
    start_time = time.time()
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download_image_async(url))
        tasks.append(task)
    await asyncio.gather(*tasks)
    end_time = time.time() - start_time
    print(f"Downloading has finished at {end_time:.2f} seconds")


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Parsers of images by URL-addresses")
    parser.add_argument(
        "--urls",
        default=data_images,
        nargs="+",
        help="List URL-addresses for downloading of images"
    )
    args = parser.parse_args()

    urls = args.urls
    if not urls:
        urls = data_images

    print(f"Downloading {len(urls)} of images - threads")
    download_images_threading(urls)

    print(f"Downloading {len(urls)} of images - multiprocessing")
    download_images_multiprocessing(urls)

    print(f"Downloading {len(urls)} of images - asynchronous")
    asyncio.run(download_images_asyncio(urls))
