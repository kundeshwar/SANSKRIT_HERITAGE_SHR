import os
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import csv
import sys

if len(sys.argv) != 4:
    print("Usage: python3 search_space21.py number start_value end_value")
    sys.exit(1)

data = [] 
sanskrit_file_link='/home/kcdh/Documents/SanskritAttribution/itihasa-main/data/dev_test.sn'
# sanskrit_file_link='/home/kcdh/Downloads/train.sn'
# itihasa_csv_file_link='/home/kcdh/Documents/SanskritAttribution/search_space_itihasa_v1.0.csv'
# itihasa_csv_file_link='/home/kcdh/Documents/SanskritAttribution/t.csv'
# with open(itihasa_csv_file_link, 'r', encoding='utf-8') as csvfile:
# 	reader = csv.reader(csvfile)
# 	f=list(reader)
f=open(sanskrit_file_link,'r').readlines()
ct=0

current=int(sys.argv[2])
end=int(sys.argv[3])#38000

f2_name='/home/kcdh/Documents/SanskritAttribution/error'+sys.argv[1]+'.txt'
f2=open(f2_name,'a')
f_res="/home/kcdh/Documents/SanskritAttribution/search_space_result"+sys.argv[1]+".csv"
n=sys.argv[1]
fcsv = open(f_res, mode='a', newline='', encoding='utf-8')
csv_writer = csv.writer(fcsv)



f_mw="/home/kcdh/Documents/SanskritAttribution/mw.csv"
mw_dict={}
with open(f_mw, 'r', encoding='utf-8') as csv_file:
	csv_reader = csv.reader(csv_file)
	for row in csv_reader:
		if len(row) >= 3:
			mw_dict[row[1]] = row[2]

num = r'[०१२३४५६७८९]'


i=0

for l1 in f:
	ct+=1
	if ct<current:
		continue
	if ct>end:
		break
	csv_writer.writerow([ct,l1[:-1]])
	# double_danda = l[:-1].split('॥')
	l1=l1.replace('।',' ')
	l3=l1.replace('।।','॥')
	l3=re.sub(r'\s+', ' ',l3)
	l3=l3.replace('ॐ','ओं') 
	l3=l3[:-1]
	l3=re.sub(num, '', l3)
	# l=l.replace('॥',' ')
	ll=l3.split('॥')
	for l in ll:
		l=l.strip()
		if l == '':
			continue
		l_velthuis=transliterate(l,sanscript.DEVANAGARI,sanscript.VELTHUIS)
		l_velthuis=l_velthuis.replace('"n','f')
		l_velthuis=l_velthuis.replace('"s','z')
		l_velthuis=l_velthuis.replace('Z','%27')
		l_velthuis=l_velthuis.replace('.a','%27')
		l_velthuis=l_velthuis.replace(' ','+')
		print(ct,l)
		csv_writer.writerow(["line",l])
		#print("kp",l)
		url='http://10.198.63.39/cgi-bin/SKT/sktreader?lex=MW&cache=t&st=t&us=f&font=roma&text='+l_velthuis+'&t=VH&topic=&mode=p&corpmode=&corpdir=&sentno='
		response = requests.get(url)
		# Check if the request was successful (status code 200)
		# print(url)
		if response.status_code == 200:
			# Get the HTML content
			# html_content = response.text
			lines = response.text.splitlines()
			hr_ct=0
			html_content=""
			#print(lines)
			for line in lines:
				if "<hr>" in line:
					hr_ct+=1
				if hr_ct == 2:
					html_content+=line+'\n'
			#print(html_content)
			word_list=[]
			root_word_list=[]
			morph_tag=[]
			meaning_link=[]
			meaning=[]
			x=0
			for l2 in html_content.splitlines()[2:]:
				t=BeautifulSoup(l2,'html.parser').get_text()
				if t.startswith('[ '):
					word_list.append(t[2:])
				elif t.startswith('['):
					root_word=t[1:t.find(']')]
					root_word_list.append(root_word)
					morph_tag.append(t[t.find('{')+1:t.find('}')])
					lnk=''
					if '{?}' not in t:
						x+=1
						lnk=l2[l2.find('href="')+7:l2.find('"><i>')]
						lnk=lnk.replace('html/','http://10.198.63.39/')
						# print(x,": ",l2,lnk,"\n")
					else:
						lnk=''
					if lnk != '':
						meaning_link.append(lnk)
						key=lnk[lnk.find('#')+1:]
						if key in mw_dict:
							meaning.append(mw_dict[key])
						else:
							meaning.append(' ')
					else:
						meaning_link.append(' ')
						meaning.append(' ')
			# shr_output=list(zip(word_list, root_word_list, morph_tag, meaning_link,meaning))
			for i in range(len(word_list)):
				csv_writer.writerow([word_list[i],root_word_list[i],morph_tag[i],meaning[i],meaning_link[i]])
			# print("\n", len(word_list), len(root_word_list), len(morph_tag), len(meaning_link), len(meaning))
			# print(shr_output)
			# data.append({'Column1': l, 'Column2': shr_output})


			# Now you can process or display the HTML content as needed python3 search_space.py
			# print(html_content)
		else:
			print(f"Failed to retrieve the webpage. Status code: {response.status_code}, trying the other option")
			url='http://10.198.63.39/cgi-bin/SKT/sktreader?lex=MW&cache=t&st=t&us=f&font=roma&text='+l_velthuis+'&t=VH&topic=&mode=t&corpmode=&corpdir=&sentno='
			response = requests.get(url)
			# Check if the request was successful (status code 200)
			# print(url)
			if response.status_code == 200:
				# Get the HTML content
				# html_content = response.text
				lines = response.text.splitlines()
				hr_ct=0
				html_content=""
				#print(lines)
				for line in lines:
					if "<hr>" in line:
						hr_ct+=1
					if hr_ct == 2:
						html_content+=line+'\n'
				#print(html_content)
				word_list=[]
				root_word_list=[]
				morph_tag=[]
				meaning_link=[]
				meaning=[]
				x=0
				for l2 in html_content.splitlines()[2:]:
					t=BeautifulSoup(l2,'html.parser').get_text()
					if t.startswith('[ '):
						word_list.append(t[2:])
					elif t.startswith('['):
						root_word=t[1:t.find(']')]
						root_word_list.append(root_word)
						morph_tag.append(t[t.find('{')+1:t.find('}')])
						lnk=''
						if '{?}' not in t:
							x+=1
							lnk=l2[l2.find('href="')+7:l2.find('"><i>')]
							lnk=lnk.replace('html/','http://10.198.63.39/')
							# print(x,": ",l2,lnk,"\n")
						else:
							lnk=''
						if lnk != '':
							meaning_link.append(lnk)
							key=lnk[lnk.find('#')+1:]
							if key in mw_dict:
								meaning.append(mw_dict[key])
							else:
								meaning.append(' ')
						else:
							meaning_link.append(' ')
							meaning.append(' ')
				# shr_output=list(zip(word_list, root_word_list, morph_tag, meaning_link,meaning))
				for i in range(len(word_list)):
					csv_writer.writerow([word_list[i],root_word_list[i],morph_tag[i],meaning[i],meaning_link[i]])
			else:
				print(f"Failed to retrieve the webpage through the second option. Status code: {response.status_code}")
				sf2=str(ct)+l+'\n'+url+'\n\n'
				f2.write(sf2)
			# result_df = pd.DataFrame(data)
			# result_df.to_csv("output_shr.csv", index=False)
			# print("saved")
			# shr_output = list("Value not found error")
			# data.append({'Column1': l, 'Column2': shr_output})

		# print(html_content)
		
		#break
# Save the DataFrame to a CSV file
# result_df = pd.DataFrame(data)
# result_df.to_csv('output_shr.csv', index=False)  # 'output.csv' is the file name

fcsv.close()
f2.close()
print(f"DataFrame saved to {f_res}")
