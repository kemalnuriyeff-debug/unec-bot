import requests

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_API = "https://openlibrary.org/search.json"


def search_google_books(query, max_results=10):
    """
    Google Books API-dən kitabları gətirir.
    """

    try:
        response = requests.get(
            GOOGLE_BOOKS_API,
            params={
                "q": query,
                "maxResults": max_results,
                "langRestrict": "en"
            },
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        books = []

        for item in data.get("items", []):

            info = item.get("volumeInfo", {})

            books.append({
                "title": info.get("title", "Naməlum"),
                "author": ", ".join(info.get("authors", ["Naməlum"])),
                "description": info.get("description", ""),
                "year": info.get("publishedDate", ""),
                "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                "source": "Google Books"
            })

        return books

    except Exception:
        return []


def search_openlibrary(query, limit=10):
    """
    Open Library API-dən kitabları gətirir.
    """

    try:

        response = requests.get(
            OPEN_LIBRARY_API,
            params={
                "q": query,
                "limit": limit
            },
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        books = []

        for doc in data.get("docs", []):

            books.append({

                "title": doc.get("title", "Naməlum"),

                "author": ", ".join(doc.get("author_name", ["Naməlum"])),

                "description": "",

                "year": doc.get("first_publish_year", ""),

                "thumbnail": None,

                "source": "Open Library"

            })

        return books

    except Exception:

        return []


def search_books(query):
    """
    Əvvəl Google Books,
    sonra Open Library.
    """

    books = search_google_books(query)

    if len(books) < 5:

        more = search_openlibrary(query)

        books.extend(more)

    return books
