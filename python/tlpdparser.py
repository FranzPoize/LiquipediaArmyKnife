import urllib.request
import re

def get_url(url):
	'''get_url accepts a URL string and return the server response code, response headers, and contents of the file'''
	req_headers = {'User-Agent': 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4'}
	request = urllib.request.Request(url, headers=req_headers) # create a request object for the URL
	response = urllib.request.urlopen(request)
	contents = response.read() # contents of the URL (HTML, javascript, css, img, etc.)
	return contents

content = get_url('http://www.franzp.fr/index.html')
trueCounter = False
commentCounter = False
map = False
winner = False
loser = False
first = True
tableTlpd = False
crack = True
for line in content.splitlines(True):
	if not tableTlpd:
		if re.search(b'tblt_table',line):
			tableTlpd = True
		else:
			continue

	if re.search(b'<!--',line):
		commentCounter = True
	
	if re.search(b'-->',line):
		commentCounter = False

	if not commentCounter:
		if (re.search(b'#B3BFD1',line) or (not first and re.search(b'#D9DDE0',line))) and not trueCounter:
			trueCounter = True
			first = False
		if re.search(b'</tr>',line) and trueCounter:
			trueCounter = False
			crack = True
	
	if trueCounter:
		if map:
			mapName = re.search(b'(?<=<a title=")[a-zA-Z0-9_\s\']*',line)
			if mapName:
				map = False
				winner = True
				print('Map : {0}'.format(mapName.group(0)))
		elif winner:
			winnerRace = re.search(b'(?<=alt="\()\w+',line)
			if winnerRace:
				print('winner : {0}'.format(winnerRace.group(0)))
				loser = True
				winner = False
		elif loser:
			loserRace = re.search(b'(?<=alt="\()\w+',line)
			if loserRace:
				print('loser : {0}'.format(loserRace.group(0)))
				loser = False
				crack = False
		if re.search(b'<img',line) and not winner and not loser and crack:
			map = True