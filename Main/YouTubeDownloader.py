import os
import yt_dlp
def download_audio_from_youtube(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join('Audios', '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            audio_id = info_dict.get('id', None)
            audio_ext = 'mp3'
            audio_path = os.path.join('Audios', f'{audio_id}.{audio_ext}')
        return audio_path

    except Exception as e:
        print("Download Error", str(e))
        return None