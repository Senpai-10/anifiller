import sys
import argparse
from lib.anime_filler_list import AnimeFillerList, EpType, colored, did_you_mean, expand_range, get_color_by_type, shows_list
from rich.console import Console
from rich.table import Table

def main():
    console = Console()

    if '-s' in sys.argv or '--shows' in sys.argv:
        shows = shows_list()

        table = Table(title=f"Available shows")

        table.add_column('Show', justify="left", no_wrap=True)

        for show in shows:
            table.add_row(show)

        console.print(table)

        exit(0)

    parser = argparse.ArgumentParser(
                prog='anifiller',
                description='Anime filler list cli tool.')

    parser.add_argument('anime_name')
    parser.add_argument('-s', '--shows', action='store_true', help="List available shows")
    parser.add_argument('-m', '--manga-canon', action='store_true')
    parser.add_argument('-M', '--mixed-canon', action='store_true')
    parser.add_argument('-f', '--filler', action='store_true')
    parser.add_argument('-a', '--anime-canon', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-H', '--hide', action='store_true', help="[Settings]: Hide titles in list table.")

    args = parser.parse_args()

    anime_name = args.anime_name

    anime_name = anime_name.strip()

    if ' ' in anime_name:
        anime_name = anime_name.replace(' ', '-')

    afl = AnimeFillerList(anime_name)
    afl.settings.hide_titles = args.hide

    if afl.connection_failure == True:
        suggestions: list[str] = did_you_mean(anime_name)

        if not len(suggestions):
            print(f"'{anime_name}' not found\nTry to run the '--shows' flag to list all available shows")
        else:
            if afl.settings.allow_colors:
                s = ", ".join(colored("cyan", str(x)) for x in suggestions)
                console.print(f"Did you mean ({s})?")
            else:
                s = ", ".join(str(x) for x in suggestions)
                print(f"Did you mean ({s})?")

        exit(1)

    if args.manga_canon == True: afl.print_list(afl.manga_canon().list)
    elif args.mixed_canon == True: afl.print_list(afl.mixed_canon().list)
    elif args.filler == True: afl.print_list(afl.filler().list)
    elif args.anime_canon == True: afl.print_list(afl.anime_canon().list)
    else: # run --list if only anime_name is provided
        table = Table(title=f"{anime_name.title()} Episode List")
        ep_list = afl.episode_list()

        for header in ep_list.headers:
            table.add_column(header, justify="left", no_wrap=True)

        for row in ep_list.body:
            if afl.settings.allow_colors == True:
                color = get_color_by_type(row.episode_type)

                table.add_row(colored(color, str(row.episode_number)),
                        colored(color, row.title), colored(color, row.episode_type.value), colored(color, row.airdate))
            else:
                table.add_row(str(row.episode_number), row.title, row.episode_type.value, row.airdate)

        console.print(table)

if __name__ == "__main__":
    main()
