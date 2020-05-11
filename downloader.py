import subprocess
import json
import asyncio
async def download_file(url):
    print(f"downloading {url}")
    process = await asyncio.create_subprocess_shell(f'youtube-dl --extract-audio --audio-format mp3 -o tmpdir/%\(title\)s\ ---\ %\(id\)s.%\(ext\)s {url}',
                                              stdout=asyncio.subprocess.PIPE)
    #process = subprocess.Popen(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', "-o", "tmpdir/%(title)s --- %(id)s.%(ext)s", url], stdout=subprocess.PIPE)

    await process.wait()
    out, err = await process.communicate()
    print(out)
    out = out.decode("utf-8")
    res = list(filter(lambda r: '[ffmpeg] Destination: ' in r, out.split('\n')))[0]
    res = res.split(' ', 2)[-1]
    print(res)
    return res

def flatten_playlist(url):
    print(f"flattening {url}")
    process = subprocess.Popen(['youtube-dl', '-j', '--flat-playlist', url], stdout=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8").strip()
    lines = out.split('\n')
    def process_line(s):
        try:
            line = json.loads(s)
            vid_url = line['url']
            title = line['title']
            link = f'https://www.youtube.com/watch?v={vid_url}'
            return {"link":link, "name":title}
        except Exception as e:
            print(e)
            print(s)

    lines = list(map(process_line, lines))
    return lines
