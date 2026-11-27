"""Stage the built Google Fonts candidates in catalog layout."""

from shutil import copyfile

from pfsans.system import ROOT


def main() -> None:
    output = ROOT / "build" / "googlefonts" / "ofl"
    families = {
        "portofaifosans": {
            "PortoFaifoSans[opsz,wght].ttf": "fonts/variable/PFSansVariable.ttf",
        },
        "portofaifomono": {
            f"PortoFaifoMono-{style}.ttf": f"fonts/mono/ttf/PFMono-{style}.ttf"
            for style in ("Regular", "Medium")
        },
    }
    for family, fonts in families.items():
        directory = output / family
        directory.mkdir(parents=True, exist_ok=True)
        for filename, source in {"OFL.txt": "OFL.txt", **fonts}.items():
            copyfile(ROOT / source, directory / filename)
    print(output)


if __name__ == "__main__":
    main()
