# Notes

## Decoder

We need to consider these cases

- The decoder was fed less info than it needs
  - e.g. the content-length was bigger than was passed as source
  - e.g. the input does not end in CRLF

- The decoder was fed more info than it needs
  - i.e. the prefix of the source was a full http request, and there might be more
