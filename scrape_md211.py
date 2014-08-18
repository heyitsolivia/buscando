import requests
from bs4 import BeautifulSoup
import csv
import time
import random






#dictionary of services in the app where values are lists of matching services in MD211

#need to find all relevant searches in MD211

resources = {"food":["Food+Stamps","Food+Pantries","Food-Home+Delivered+Groceries","Food+Supplements","Food+Vouchers","Donor+Services-Food"],
			"clothing":["Clothing-Clothing+Closet","Clothing-School+Uniforms","Donor+Services-Clothing","Clothing-Work+Attire"],
			"legal services":["Legal+Services-Immigrant+Community","Legal+Services-Lawyer+Referral"],"language":["English+as+a+Second+Language","Interpretation\%\2c+Translation"],
			"medical care":["Pediatrics","Eye+Care","Allergies","Hospitals","Dental+Care"],
			"education and enrollment":["Education-At+Risk+Youth","Education-Early+Childhood","Education-Elementary\%\2c+Secondary","Education-Special","School+Supplies","Summer+School","Tutorial+Services","After+School+Programs"],
			"religious services":["Counseling-Pastoral\%\2c+Spiritual"],
			"transportation":["Transportation-Low+Income", "Transportation-Medical", "Transportation-Mental+Illness", "Transportation-Open+To+Public"],
			"counseling":["Counseling-Pastoral\%\2c+Spiritual","Counseling-Hispanic\%\2c+Latino+Community","Counseling-Child+Sexual+Assault","Counseling-Youth"],
			"recreation":["Camps","Recreation-Youth","Recreation-Parent\%\2c+Child","Therapeutic+Recreation","Physical+Fitness","After+School+Programs","Youth+Development"],
			"volunteers":["Volunteer+Opportunities","Information\%\2c+Referral-Volunteer"]}



#build the URL

orgs = {} #a dict of dicts where key is the org name plus the address as a tuple and values are dictionaries containing name, address and each resource

for r in resources:
	for web_name in resources[r]:
		#something about pages here
		
		validator = ''
		page = 1
		while validator == '':
			url =   "http://www.icarol.info/Search.aspx?org=2046&Count=5&Search={0}\
				&NameOnly=True&pst=Coverage&sort=Proximity&TaxExact=False&Country=United+States\
				&StateProvince=MD&County=-1&City=-1&page={1}".format(web_name, page)

			print("resource: {0}, page: {1}".format(web_name,page))
			

		
			time.sleep(random.randint(1,3)) #apparently dirk had some trouble being kicked out
				#so we're going to take a random-length timeout between each time we hit the website
				#this will make the script really slow, but we only have to run it once, so nbd.
			
			response = requests.get(url)
			soup = BeautifulSoup(response.text)
		
			validator = soup.find("span",attrs={"class":"Validator"}).text
			if validator == '':

				#print(soup.prettify())
		
				#the website doesn't seem to have a container that holds both the name of the org and the
				#contact info together, so we're counting on them being in the same order.
				header_info = soup.findAll('td',attrs={"class":"DetailsHeader"})
				address_info = soup.findAll('td',attrs={"class":"SearchDetails"})
				if len(header_info) != len(address_info):
					print "Error: Could not scrape page {0}".format(page)
				
				else:
				#maybe should throw an error if they're not the same length
		
					for i in range(len(header_info)):
						h = header_info[i].text.strip()
						a = address_info[i]
						org_name = h[h.find("Agency")+8:]
						

						#there is inconsistent info on MD211, so the try/excepts deal with potential missing data

						address_label = "rptSearchResults_lblAddress_{0}".format(i)
						try:
							address = a.find('span', attrs={"id":address_label}).text.strip()
						except AttributeError:
							address = ''
							
						try:	
							lblcity = a.find('span', attrs={"id":"rptSearchResults_lblCity_{0}".format(i)}).text.strip()
							#this is actually city, state, zip and country and needs to be parsed
							#we remove country since it's always US, then strip out the extra space and use rsplit to split on the first two spaces from the right
							lblcity = lblcity[:lblcity.find("United States")].strip().rsplit(" ",2)
							
							city = lblcity[0]
							state = lblcity[1]
							zipcode = lblcity[2]

						except AttributeError:
							city = ''
							state = ''
							zipcode = ''
						
						phone_label = "rptSearchResults_lblPhone_{0}".format(i)
						try:
							phone = a.find('span', attrs={"id":phone_label}).text.strip("Phone:").strip()
						except AttributeError:
							phone = ''
			
				
						website_label = "rptSearchResults_hlAgencyName_{0}".format(i)
						try:
							website = a.find('a',attrs={"id":website_label}).text.strip()
						except AttributeError:
							website = ''
						

				
						org_key = (org_name,address)
				
						if org_key not in orgs:
							orgs[org_key] = {"provider_name":org_name,
								"address1":address,"city":city, "state":state,
								"zipcode":zipcode,"phone":phone,"website":website}
				
						orgs[org_key][r] = "yes"
				
				
				
			
					#print(len(header_info))
					#print(len(address_info))
					#print orgs
				page += 1



#dump dictionary to a properly formatted csv

csv_header = ["provider_name","location_name","image","website","address1","address2","city","state",
			"zipcode","contact","phone","hours","food","clothing","legal services","language",
			"medical care","education and enrollment","religious services","transportation",
			"counseling","housing","recreation","volunteers","other"]



with open("providers_from_md211.csv","wb") as provider_csv:
	w = csv.DictWriter(provider_csv, csv_header)
	w.writer.writerow(csv_header)
	for key,row in orgs.iteritems():
		w.writerow(row)
	