import argparse
from anime_filler_list import AnimeFillerList, expand_range, get_color_by_type
from rich.console import Console
from rich.table import Table

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                prog='anifiller',
                description='Anime filler list cli tool.')

    parser.add_argument('anime_name')

    parser.add_argument('-m', '--manga-canon', action='store_true')
    parser.add_argument('-M', '--mixed-canon', action='store_true')
    parser.add_argument('-f', '--filler', action='store_true')
    parser.add_argument('-a', '--anime-canon', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-H', '--hide', action='store_true', help="[Settings]: Hide titles in list table.")

    parser.add_argument('-t', '--type', help="Check episode/s type/s, example: '--type 1 2 3 4 5-15'", action="extend", nargs="+", type=str)

    args = parser.parse_args()
    console = Console()

    if ' ' in args.anime_name:
        args.anime_name = args.anime_name.replace(' ', '-')

    afl = AnimeFillerList(args.anime_name)
    afl.settings.hide_titles = args.hide

    afl.start()

    if args.manga_canon == True: afl.print_list(afl.manga_canon.list)
    elif args.mixed_canon == True: afl.print_list(afl.mixed_canon.list)
    elif args.filler == True: afl.print_list(afl.filler.list)
    elif args.anime_canon == True: afl.print_list(afl.anime_canon.list)
    elif args.list == True:
        table = Table(title=f"{args.anime_name.title()} Episode List")

        for header in afl.episode_list.headers:
            table.add_column(header, justify="left", no_wrap=True)

        for row in afl.episode_list.body:
            table.add_row(*row)

        console.print(table)

    if args.type != None:
        headers = ["#", "type"]
        body = []

        for ep in args.type:
            if '-' in ep:
                eps = expand_range(ep)

                for j in eps:
                    ep_type = afl.check_type(j)
                    if afl.settings.allow_colors == True:
                        color = get_color_by_type(ep_type)
                        ep_type = f"[{color}]{ep_type}[/ {color}]"

                    body.append([str(j), str(ep_type)])
            else:
                ep_type = afl.check_type(int(ep))

                if afl.settings.allow_colors == True:
                    color = get_color_by_type(ep_type)
                    ep_type = f"[{color}]{ep_type}[/ {color}]"

                body.append([str(ep), str(ep_type)])

        table = Table(title="Episode type list")

        for header in headers:
            table.add_column(header, justify="left", no_wrap=True)

        for row in body:
            table.add_row(*row)

        console.print(table)
