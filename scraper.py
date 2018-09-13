import requests
from bs4 import BeautifulSoup
import os
import json

url = 'https://etherscan.io/contractsVerified/2'
page_number = 1729

if not os.path.exists('./contracts'):
    os.makedirs('./contracts')

for page in xrange(1,1729):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    for contract in soup.tbody.find_all('tr'):
        cellsArray = contract.find_all('td')

        contract_address = contract.a.get_text()
        contract_url = contract.a.get('href')
        contract_name = cellsArray[1].get_text()
        contract_balance = cellsArray[3].get_text()

        directory = './contracts/' + contract_name

        try :
            balance = float(contract_balance.replace(",", "").split()[0])
        except :
            continue

        if not balance > 0:
            continue

        if not os.path.exists(directory):
            os.makedirs(directory)
            url = 'https://etherscan.io' + contract_url
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            editor = soup.find(id='editor')
            f =  open(directory + '/contract.sol', 'w')
            try :
                code = editor.get_text()
            except Exception as err:
                print contract_address
                os.remove(directory + '/contract.sol')
                os.rmdir(directory)
                f = open('failed.txt', 'w')
                f.write(contract_address + '\n')
                f.close()
                continue

            if code :
                f.write(code.encode('utf-8'))
            f.close()

            f = open(directory + '/info.json', 'w')
            details = [{"address": contract_address, "balance": contract_balance}]
            f.write(json.dumps(details))
            f.close()
        else:
            # Check hash to be sure it is the same contract
            f = open(directory + '/info.json', 'rw+')
            detail = {"address": contract_address, "balance": contract_balance}
            details = json.loads(f.read())
            details.append(detail)
            f.seek(0)
            f.write(json.dumps(details))
            f.truncate()
            f.close()


    print 'Count : ' + str(page) + '/' + str(page_number)
    url = 'https://etherscan.io/contractsVerified/' + str(page)
