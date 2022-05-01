from cookies import save_cookie, check_cookie
from typing import List
from Recording import Recording
import os
from Config import Config
from parsers import recordings_from_html
from parsers import recordings_from_txt
from xlsx import generate_xlsx
import typer
import pathlib
from aria2c import aria2c_download
from generate_download_links_file import generate_download_links_file
import re


app: typer.Typer = typer.Typer(add_completion=False)


@app.command(
    help="Download Polimi lessons recordings from the recordings archives HTML."
)
def html(
    file: str = typer.Argument(..., help="The input file"),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True, help="Download with aria2c or just create a file with the download links"
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from the recordings archives HTML."""
    # Option check
    if not (os.path.isfile(file)):
        typer.echo(f"The file {file} does not exists.")
        raise typer.Exit(code=1)

    # Check cookies
    check_cookie("SSL_JSESSIONID")
    check_cookie("ticket")

    # Get recordings
    typer.echo("Recordings parsing from HTML started...")
    recordings: List[Recording] = recordings_from_html(file)

    # Output
    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def urls(
    file: str = typer.Argument(..., help="The input file"),
    course: str = typer.Option(..., help="The course name"),
    academic_year: str = typer.Option(
        ..., help='The course academic year in the format "2021-22"'
    ),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True, help="Download with aria2c or just create a file with the download links"
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from a list of urls."""
    # Optio check
    if not (os.path.isfile(file)):
        typer.echo(f"The file {file} does not exists.")
        raise typer.Exit(code=1)

    # Check cookies
    check_cookie("SSL_JSESSIONID")

    academic_year_r = re.compile("^[0-9]{4}-[0-9]{2}$")
    if academic_year_r.match(academic_year) is None:
        typer.echo('The course academic year must be in the format "2021-22".')
        raise typer.Exit(code=1)

    # Get recordings
    recordings: List[Recording] = recordings_from_txt(file, course, academic_year)

    # Output
    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


def create_output(
    recordings: List[Recording], output: str, create_xlsx: bool, aria2c: bool
) -> None:
    """Create the output.

    Args:
        recordings (List[Recording]): The recordings.
        output (str): The output path.
        create_xlsx (bool): True to create xlsx. Defaults to True.
        aria2c (bool): True to download with aria2c. Defaults to True.
    """
    typer.echo(f"Found {len(recordings)} recordings.")
    if len(recordings) > 0:
        # Generate xlsx
        if create_xlsx:
            typer.echo("Generating xlsx files...")
            generate_xlsx(recordings, output)

        # aria2c download
        if aria2c:
            typer.echo("Starting download with aria2c...")
            aria2c_download(recordings, output)
        else:
            generate_download_links_file(recordings, output)


@app.command(help="Set the value of a cookie.")
def set_cookie(
    name: str = typer.Argument(
        ..., help='Cookie name. Possible values are "SSL_JSESSIONID" and "ticket"'
    ),
    value: str = typer.Argument(..., help="Cookie value."),
) -> None:
    """Set the value of a cookie."""
    # Arguments check
    if name != "SSL_JSESSIONID" and name != "ticket":
        typer.echo(
            f'The name of the cookie is invalid, possible values are "SSL_JSESSIONID" and "ticket".'
        )
        raise typer.Exit(code=1)

    save_cookie(name, value)
    typer.echo(f"Cookie {name} set to {value}.")


if __name__ == "__main__":
    if not os.path.exists(typer.get_app_dir(Config.APP_NAME)):
        os.makedirs(typer.get_app_dir(Config.APP_NAME))

    app()
