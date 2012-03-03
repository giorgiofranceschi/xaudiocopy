import re

artist="The Cranberries"
album="No Need to Argue"
year = str(1995)
track_number=14
#title="Ode to my Family"

pattern = "%a/[%y] %a - %d/%n - &t.mp3"
pattern = re.compile("%a").sub(artist, pattern)
pattern = re.compile("%d").sub(album, pattern)
pattern = re.compile("%y").sub(year, pattern)
pattern = re.compile("%n").sub(str('%(#)02d' %{"#": track_number}), pattern)
pattern = re.compile("%t").sub(title, pattern)

print pattern