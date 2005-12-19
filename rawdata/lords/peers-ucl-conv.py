import re


lordnametoofnameids = re.findall('"uk.org.publicwhip/lord/(\d+)"', """
<lordnametoofname id="uk.org.publicwhip/lord/100415" title="Earl" name="Mar and Kellie"/>
<lordnametoofname id="uk.org.publicwhip/lord/100465" title="Earl" name="Northesk"/>
<lordnametoofname id="uk.org.publicwhip/lord/100197" title="Earl" name="Erroll"/>
<lordnametoofname id="uk.org.publicwhip/lord/100473" title="Earl" name="Onslow"/>
<lordnametoofname id="uk.org.publicwhip/lord/100099" title="Earl" name="Caithness"/>
<lordnametoofname id="uk.org.publicwhip/lord/100375" title="Earl" name="Listowel"/>
<lordnametoofname id="uk.org.publicwhip/lord/100569" title="Earl" name="Sandwich"/>
<lordnametoofname id="uk.org.publicwhip/lord/100181" title="Earl" name="Dundee"/>
<lordnametoofname id="uk.org.publicwhip/lord/100377" title="Earl" name="Liverpool"/>
<lordnametoofname id="uk.org.publicwhip/lord/100578" title="Earl" name="Selborne"/>
<lordnametoofname id="uk.org.publicwhip/lord/100020" title="Earl" name="Arran"/>
<lordnametoofname id="uk.org.publicwhip/lord/100835" title="Earl" name="Glasgow"/>
<lordnametoofname id="uk.org.publicwhip/lord/100145" title="Earl" name="Courtown"/>
<lordnametoofname id="uk.org.publicwhip/lord/100591" title="Earl" name="Shrewsbury"/>
<lordnametoofname id="uk.org.publicwhip/lord/100551" title="Earl" name="Rosslyn"/>
<lordnametoofname id="uk.org.publicwhip/lord/100372" title="Earl" name="Lindsay"/>
<lordnametoofname id="uk.org.publicwhip/lord/100480" title="Viscount" name="Oxfuird"/>
<lordnametoofname id="uk.org.publicwhip/lord/100729" title="Earl" name="Longford"/>
<lordnametoofname id="uk.org.publicwhip/lord/100713" title="Earl" name="Carnarvon"/>
<lordnametoofname id="uk.org.publicwhip/lord/100604" title="Earl" name="Snowdon"/>
<lordnametoofname id="uk.org.publicwhip/lord/100300" title="Earl" name="Home"/>
""")




fin = open("peers-ucl-2005-12-03.txt", "r")
lordlines = fin.readlines()
fin.close()

fout = open("peers-ucl.xml", "w")
fout.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
fout.write('\n\n<!-- Generated by peers-ucl-conv.py from database dump of the house made on 2005-12-03 -->\n\n\n')
fout.write('<publicwhip>\n\n')

assert lordlines[0] == '"id","title","forename","surname","region","party","type","oath_date","died_retired_date","year_created","d_o_b","Hansard_name","ex_MP"\n'
attrlist = None

"""<lord
	id="uk.org.publicwhip/lord/1000000"
	house="lords"
	title="Queen" lordname="Elizabeth" lordofname="Windsor"
	frontnames=""
	peeragetype="Monarch" affiliation="Crown"
	fromdate="1954-01-30"
	source=""
	comment=""
/>
"""

titleconv = {  'L.':'Lord',
			   'B.':'Baroness',
			   'Abp.':'Archbishop',
			   'Bp.':'Bishop',
			   'V.':'Viscount',
			   'E.':'Earl',
			   'D.':'Duke',
			   'M.':'Marquess',
			   'C.':'Countess',
			   'Ly.':'Lady',
			}

parties = [ 'Con', 'Lab', 'Dem', 'XB', 'Other', 'Bp', 'None' ]
types = [ 'HD', 'A', 'L', 'HP', 'B', 'HO' ]

#"id","title","forename","surname","region","party","type","oath_date","died_retired_date","year_created","d_o_b","Hansard_name","ex_MP"
#1,"Lord","Morys","Aberdare",,"Con","HD",,23/01/2005 00:00:00,1957,16/06/1919 00:00:00,"Aberdare, L.","N"

for lordline in lordlines:
	ss = re.findall('(?:"([^"]*)"|([^,]*))[,\n]', lordline)
	s = [ l[0] or l[1]  for l in ss ]
	assert len(s) == 13
	if not attrlist:
		attrlist = s
		continue

	lordattr = {}
	for (a, b) in zip(attrlist, s):
		lordattr[a] = b

	# try to decode the relationship between the hansard name
	# (which is incomplete -- it's what appears in the divisions, but doesn't distinguish "Lord Arran" from "The Lord of Arran"
	# Meanwhile, the surnames are not always part of the name.  We're in a mess
	Hansard_name = lordattr['Hansard_name']
	Hansard_nameMatch = re.match("([^,()]*?)(?:\sof\s([^,()]*?))?\s*(\(now [^)]*\))?, ([ALBVEDCMLybp]+\.)$", Hansard_name)

	lordname = Hansard_nameMatch.group(1) or ""
	lordofname = Hansard_nameMatch.group(2) or ""

	# predict the title from the hansard pattern
	title = titleconv[Hansard_nameMatch.group(4)]
	predictedlordtitle = title
	if title in ["Archbishop", "Bishop", "Marquess", "Countess", "Duke"]:
		predictedlordtitle += " of"

		# migrate to the of-name
		assert not lordofname
		lordofname = lordname
		lordname = ""

	assert lordattr['title'] == predictedlordtitle

	if lordattr['region']:
		lordofnameMatch = re.match("\s*(of|de) (.+)$", lordattr['region'])
		if lordofnameMatch.group(1) == "de":
			pass # already ends with it lordname += " de " + lordofnameMatch.group(2)  # merge in de's with the main name
		else:
			lordofname = lordofnameMatch.group(2)

	# remove dots
	lordname = re.sub("\.", "", lordname)
	lordname = re.sub("^De ", "de ", lordname)
	lordofname = re.sub("\.", "", lordofname)

	party = lordattr['party']
	if not party:
		party = 'None'
	assert party in parties

	ltype = lordattr['type']
	assert ltype in types

	assert (ltype == "B") == (party == "Bp")


	fromdate = lordattr['year_created']
	if lordattr['oath_date']:
		oath_dateMatch = re.match('(\d\d)/(\d\d)/(\d\d\d\d) 00:00:00$', lordattr['oath_date'])
		#if (oath_dateMatch.group(3) != fromdate):  print lordline  # does not always match quite
		fromdate = '%s-%s-%s' % (oath_dateMatch.group(3), oath_dateMatch.group(2), oath_dateMatch.group(1))
	assert fromdate

	if lordattr['died_retired_date']:
		died_retired_dateMatch = re.match('(\d\d)/(\d\d)/(\d\d\d\d) 00:00:00$', lordattr['died_retired_date'])
		todate = '%s-%s-%s' % (died_retired_dateMatch.group(3), died_retired_dateMatch.group(2), died_retired_dateMatch.group(1))
	else:
		todate = '9999-12-31'


	slordid = "%d" % (100000 + int(lordattr['id']))

	# do some corrections we've pulled out of the data
	if slordid in lordnametoofnameids:  # lordofname distinctions not in the data
		assert not lordofname and lordname
		lordofname = lordname
		lordname = ""

	# posssibly incorrect title
	if (title, lordname, lordofname) == ("Baroness", "Young", "Dartington"):
		title = "Lord"
	if (title, lordname, lordofname) == ("Bishop", "", "Blackburn"): # possibly a previous bishop though
		fromdate = "1999-11-11"
	if (title, lordname, lordofname) == ("Bishop", "", "Wakefield"): # speaks on 2005-03-22
		todate = "2005-03-22"
	if (title, lordname, lordofname) == ("Bishop", "", "Newcastle"): # votes on 2002-11-05
		fromdate = "2002-11-05"


	assert fromdate < todate


	#if not lordattr['d_o_b']:  # missing in a couple of cases
	#	print lordline

	fout.write('<lord\n')
	fout.write('\tid="uk.org.publicwhip/lord/%s"\n' % slordid)
	fout.write('\thouse="lords"\n')
	fout.write('\tforenames="%s"\n' % lordattr['forename'])
	fout.write('\ttitle="%s" lordname="%s" lordofname="%s"\n' % (title, lordname, lordofname))
	fout.write('\tpeeragetype="%s" affiliation="%s"\n' % (ltype, party))
	fout.write('\tfromdate="%s" todate="%s"\n' % (fromdate, todate))
	if lordattr['ex_MP'] == 'Y':
		fout.write('\tex_MP="yes"\n')

	fout.write('/>\n')

fout.write("\n</publicwhip>\n")
fout.close()



