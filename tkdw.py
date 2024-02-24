import argparse
import json
import os.path

import constants


def main():
    parser = argparse.ArgumentParser(
        prog="tkdw",
        description="TkDecentralizedWhisper. Licensed by AGPLv3 or higher.",
        epilog="Visit https://github.com/thiliapr/TkDecentralizedWhisper to get more information."
    )
    parser.add_argument("-c", "--config", dest="cfg_file",
                        default="config.json", type=str, help="Configuration file.")
    parser.add_argument("--initialize", dest="initialize", action="store_true", default=False,
                        help="Initialize the configuration file.")
    args = parser.parse_args()

    # Initialize configuration
    if args.initialize:
        with open(args.cfg_file) as f:
            json.dump(constants.default_config, f)

        print("Default configuration has been written to file `{}`.".format(args.config))
        return

    # Read config
    if (not os.path.exists(args.cfg_file)) or (not os.path.isfile(args.cfg_file)):
        print("Configuration file `{}` not found. Please run `tkdw --initialize` to initialize the configuration file.")
    with open(args.cfg_file, mode="r", encoding="utf-8") as f:
        config: dict = json.load(f)


if __name__ == "__main__":
    main()
