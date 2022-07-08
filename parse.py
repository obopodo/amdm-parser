from src import Parser
import sys

if __name__ == '__main__':
    parser = Parser()
    args = sys.argv[1:]
    artist, song = args[:2]
    songs_list = parser.get_songs_list(artist, song)

    if len(args) == 3:
        song_index = int(args[2])
        song_name, song_text = parser.parse_song_page(
            parser.get_song_url_by_index(songs_list, song_index)
        )
        print(song_name)
        print(song_text)

    if len(args) == 4:
        song_index = int(args[2])
        folder = args[3]
        song_index = int(args[2])
        song_name, song_text = parser.parse_song_page(
            parser.get_song_url_by_index(songs_list, song_index)
        )

        parser.save_to_file(
            folder, 
            song_name,
            song_text)

