import subprocess
def download_file(url):
    process = subprocess.Popen(['youtube-dl', '--extract-audio', '--audio-format', 'mp3', url], stdout=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8")
    res = list(filter(lambda r: '[ffmpeg] Destination: ' in r, out.split('\n')))[0]
    res = res.split(' ', 2)[-1]
    return res
