from lxml import html, cssselect
import sys

tableSel = cssselect.CSSSelector('div.hashi>table>tbody')
def grab(url):
    print('load page:', url)
    root = html.parse(url)
    print('page loaded')
    try:
        tab = tableSel(root)[0]
    except IndexError:
        print(html.tostring(root, pretty_print=True).decode(), file=open('dump.html', 'w'))
        print('no hashi table found on page, page dumped to dump.html', file=sys.stderr)
        exit(1)
    a = []
    for row in tab.findall('tr'):
        line = ''.join(d.text for d in row.findall('td'))
        a.append(line)
    a = '\n'.join(a)
    print(a)
    return a

# sizes = [7, 9, 11, 13, 17, 20, 25]
# urlTemp = 'http://www.menneske.no/hashi/{0}x{0}/eng/'
# urlDefault = 'http://www.menneske.no/hashi/eng/'
# # url2 = 'puzzles/puzzles.htm'
# size = int(sys.argv[1])
# if size not in sizes:
#     print('{0} not in {1}'.format(size, sizes), file=sys.stderr)
#     exit(1)
# if size != 11:
#     url = urlTemp.format(size)
# else:
#     url = urlDefault
url = sys.argv[1]
with open(sys.argv[2], 'w') as outfile:
    print(grab(url), file=outfile)
print('saved to', sys.argv[2])
