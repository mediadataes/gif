import urllib.request

jq_file = __file__[:-2]+"js"

def main():
    from asyncio import get_event_loop
    get_event_loop().run_until_complete(download())
    print("Done")

async def download(file_name:str=jq_file, return_after:bool=False, *,
            url:str="https://code.jquery.com/jquery-latest.min.js"):
    print("Downloading jQuery...")
    if(return_after):
        text = f"{''.join([a.decode('utf-8') for a in urllib.request.urlopen(url).readlines()[1:]])[:-1]}"
        with open(file_name,'w') as file:
            file.write(text)
        print("Done (jQuery download)")
        return text

    with open(file_name,'w') as file:
        file.write(f"{''.join([a.decode('utf-8') for a in urllib.request.urlopen(url).readlines()[1:]])[:-1]}")
        print("Done (jQuery download)")

async def load(file_name:str=jq_file):
    return open(file_name, 'r').read()

if __name__ == "__main__":
    main()