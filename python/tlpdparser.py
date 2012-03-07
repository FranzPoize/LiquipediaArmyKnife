import urllib.request
import re
import time

def get_url(url):
	'''get_url accepts a URL string and return the server response code, response headers, and contents of the file'''
	req_headers = {'Cookie' : '__qca=P0-843648291-1308859660383; SID=21b580a941315f6a063e351ae731fb33; tlnet=GD-g75q4NJXiH1nRCXfhICbIOh2Yp0TQN0mWekj8syhqIL6nSm1_Sf26CgT4r9LoQ4ZtjLqZ1JQ7JJjF3Cah2rOIWjmyHSdYyBpUUDIS1geZMCE; __utma=30386106.146671338.1309791220.1331144242.1331150649.339; __utmb=30386106.10.10.1331150649; __utmc=30386106; __utmz=30386106.1324085285.320.228.utmcsr=reddit.com|utmccn=(referral)|utmcmd=referral|utmcct=/r/starcraft/comments/nfgiy/hi_im_2gd_a_host_commentator_event_organizer_ex/'
	,'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}
	request = urllib.request.Request(url, headers=req_headers) # create a request object for the URL
	response = urllib.request.urlopen(request)
	contents = response.read() # contents of the URL (HTML, javascript, css, img, etc.)
	return contents
	
class statTable:
	def __init__(self):
		self.mapList = {}
		self.mapList[b'Total'] = [[0,0],[0,0],[0,0]]
	
	def addResult(self,mapName,winner,loser):
		if mapName not in self.mapList:
			self.mapList[mapName] = [[0,0],[0,0],[0,0]]
		#order of mapResult is PvT,PvZ,TvZ
		pvt,pvz,tvz = self.mapList[mapName] 
		pvtT,pvzT,tvzT = self.mapList[b'Total'] 
		if winner in b'P':
			if loser in b'T':
				pvt[0] += 1
				pvtT[0] += 1
			elif loser in b'Z':
				pvz[0] +=1
				pvzT[0] +=1
		elif winner in b'Z':
			if loser in b'T':
				tvz[1] +=1
				tvzT[1] +=1
			elif loser in b'P':
				pvz[1] +=1
				pvzT[1] +=1
		elif winner in b'T':
			if loser in b'P':
				pvt[1] +=1
				pvtT[1] +=1
			elif loser in b'Z':
				tvz[0] +=1
				tvzT[0] +=1

def parseContent(content,results):
	trueCounter = False
	commentCounter = False
	map = False
	winner = False
	loser = False
	first = True
	tableTlpd = False
	crack = True
	add = False
	page = False
	action = False
	count = 0
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
				mapName = re.search(b'(?<=<a title=")[a-zA-Z0-9_\s\'\.]*',line)
				if mapName:
					map = False
					winner = True
					mapNameString = mapName.group(0)
			elif winner:
				winnerRace = re.search(b'(?<=alt="\()\w+',line)
				if winnerRace:
					winnerRaceStr = winnerRace.group(0)
					loser = True
					winner = False
			elif loser:
				loserRace = re.search(b'(?<=alt="\()\w+',line)
				if loserRace:
					loserRaceStr = loserRace.group(0)
					add = True
					loser = False
					crack = False
					count = count + 1
			if re.search(b'<img',line) and not winner and not loser and crack:
				map = True
				
		if page:
			actionRe = re.search(b'(?<=remote_query\()[a-zA-Z0-9,\']*',line)
			if actionRe:
				page = False
				action = actionRe.group(0)
		if re.search(b'name="tabulator_page"',line):
			page = True
				
		if add:
			results.addResult(mapNameString,winnerRaceStr,loserRaceStr)
			add = False
	if action:
		return action

url = 'http://www.teamliquid.net/tlpd/details.php?section=sc2-international&type=leagues&id=1889&part=games&tabulator_order_col=1&tabulator_order_desc=1&tabulator_search=&tabulator_page='

results = statTable()
page = b'1'
while True:
	print(url+page.decode())
	content = get_url(url + page.decode())
	response = parseContent(content,results)
	if response:
		cont,id,page,fuck,order = re.findall(b'[0-9A-Za-z]+',response)
		print(page)
		time.sleep(1)
		response = None
		print('First request over')
	else:
		print('end')
		break

print(results.mapList)

f = open('result.txt', 'w')
maps = ''
scorePvT = '|\'\'\'PvT\'\'\'||'
scorePvZ = '|\'\'\'PvZ\'\'\'||'
scoreTvZ = '|\'\'\'TvZ\'\'\'||'

for key,values in results.mapList.items():
	maps += '![[' + key.decode() + ']]\n'
	scorePvT += str(values[0][0]) + '-' + str(values[0][1]) +'||'
	scorePvZ += str(values[1][0]) + '-' + str(values[1][1]) +'||'
	scoreTvZ += str(values[2][0]) + '-' + str(values[2][1]) +'||'
	
f.write('''{| class="wikitable"
! Test
'''+maps+'\n|-\n'+scorePvT+'\n|-\n'+scorePvZ+'\n|-\n'+scoreTvZ+'\n|}')