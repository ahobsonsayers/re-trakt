import time

import requests
from trakt.api import HttpClient, TokenAuth  # type: ignore
from trakt.auth.pin import PinAuthAdapter  # type: ignore
from trakt.config import AuthConfig  # type: ignore
from trakt.movies import Movie  # type: ignore
from trakt.sync import get_collection, remove_from_collection  # type: ignore


def main():
    trakt_client = get_client()
    auth_config = get_auth_config()
    authenticate(trakt_client, auth_config)
    remove_collected_movies()


def get_client() -> HttpClient:
    session = requests.Session()
    return HttpClient("https://api.trakt.tv/", session)


def get_auth_config() -> AuthConfig:
    auth_config = AuthConfig(".trakt")
    auth_config.CLIENT_ID = None
    auth_config.CLIENT_SECRET = None
    auth_config.OAUTH_EXPIRES_AT = None
    auth_config.OAUTH_REFRESH = None
    auth_config.OAUTH_TOKEN = None
    auth_config.load()

    if not auth_config.APPLICATION_ID or not auth_config.CLIENT_ID or not auth_config.CLIENT_SECRET:
        print("\nApplication detail are required.")
        print("You can obtain them from https://trakt.tv/oauth/applications\n")
        if auth_config.APPLICATION_ID is None:
            auth_config.APPLICATION_ID = input("Enter your Trakt application ID: ")
        if auth_config.CLIENT_ID is None:
            auth_config.CLIENT_ID = input("Enter your Trakt client ID: ")
        if auth_config.CLIENT_SECRET is None:
            auth_config.CLIENT_SECRET = input("Enter your Trakt client secret: ")

    return auth_config


def authenticate(client: HttpClient, auth_config: AuthConfig) -> None:
    if getattr(auth_config, "OAUTH_TOKEN", None) is None:
        # Authenticate
        pin_auth = PinAuthAdapter(
            client=client,
            config=auth_config,
        )
        pin_auth.authenticate()

        # Store auth config
        auth_config.store()

    # Update client to use auth
    client.auth = TokenAuth(client=get_client, config=get_auth_config)


def remove_collected_movies() -> None:
    print("Fetching your movie collection...")

    movies: list[Movie] = get_collection(list_type="movies")
    if not movies:
        print("No movies found in your collection.")
        return

    num_movies = len(movies)
    print(f"WARNING: This will permanently remove {num_movies} movies from your collection.")
    confirm = input("Continue? (y/n): ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    print("Removing movies...\n")

    for collected_movie in movies:
        remove_from_collection(collected_movie)
        print(f"Removed {collected_movie.title}")
        time.sleep(1)

    print(f"\nSuccessfully removed {num_movies} movies from your collection!")


if __name__ == "__main__":
    main()
